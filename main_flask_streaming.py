from flask import Flask, request, jsonify, send_from_directory
from pyzbar.pyzbar import decode
import numpy as np
import cv2
import base64

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory("templates", "index2.html")

@app.route("/process", methods=["POST"])
def process_frame():
    data = request.json.get("image")
    if not data:
        return jsonify({"error": "No image provided"}), 400

    # Entferne header (data:image/jpeg;base64,...)
    header, encoded = data.split(",", 1)
    img_data = base64.b64decode(encoded)
    nparr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # QR-Codes erkennen
    decoded_objects = [obj for obj in decode(frame) if obj.type == 'QRCODE']
    for obj in decoded_objects:
        qr_data = obj.data.decode('utf-8')
        print("Gefunden:", qr_data)
        points = obj.polygon
        hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
        hull = list(map(tuple, np.squeeze(hull)))
        for j in range(len(hull)):
            pt1 = tuple(map(int, hull[j]))
            pt2 = tuple(map(int, hull[(j + 1) % len(hull)]))
            cv2.line(frame, pt1, pt2, (0, 0, 255), 2)

        cv2.putText(frame, qr_data, (obj.rect.left, obj.rect.top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jsonify({"image": "data:image/jpeg;base64," + jpg_as_text})


if __name__ == "__main__":
    app.run(debug=True)
