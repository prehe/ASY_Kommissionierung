import cv2
from pyzbar.pyzbar import decode
import numpy as np

def highlight_product_qrcodes_from_job(cap, product_names: list = None):
    print("QR-Code-Scanner gestartet. Drücke 'q' zum Beenden.")
    
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Nur QR-Codes erkennen (kein PDF417, keine Barcodes)
        decoded_objects = [obj for obj in decode(frame) if obj.type == 'QRCODE']

        for obj in decoded_objects:
            # Daten aus QR-Code extrahieren
            qr_data = obj.data.decode('utf-8')

            # Rechteck um QR-Code zeichnen, wenn QR-Code-Daten mit product_names übereinstimmen
            if qr_data in product_names:
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    hull = list(map(tuple, np.squeeze(hull)))
                else:
                    hull = points

                n = len(hull)
                for j in range(0, n):
                    cv2.line(frame, hull[j], hull[(j + 1) % n], (0, 0, 255), 2)

                # Text anzeigen (nur für gültige QR-Codes)
                cv2.putText(frame, qr_data, (obj.rect.left, obj.rect.top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Bild anzeigen
        cv2.imshow('QR-Code Scanner', frame)

        # Beenden mit Taste 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def scan_new_job(cap):
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Nur QR-Codes erkennen (kein PDF417, keine Barcodes)
        decoded_objects = [obj for obj in decode(frame) if obj.type == 'QRCODE']

        for obj in decoded_objects:
            # Daten aus QR-Code extrahieren
            qr_data = obj.data.decode('utf-8')
            return str(qr_data) 

        # Bild anzeigen
        cv2.imshow('QR-Code Scanner', frame)
        
        # Beenden mit Taste 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break