import cv2
from ASY_QRCode_Erkennung import highlight_product_qrcodes_from_job, scan_new_job

def init_camera():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print(f"Kamera 0 konnte nicht geöffnet werden.")
        assert False, "Kamera konnte nicht geöffnet werden."
    return cap

def close_window(cap):
    cap.release()
    cv2.destroyAllWindows()

def main():
    # Kameraauswahl: 0 = Frontkamera, 1 = Rückkamera (je nach Gerät anpassen)
    cap = init_camera()

    job_id = scan_new_job(cap)
    print(f"Neuer Job-ID: {job_id}")
    # Warte auf QR-Code-Scan für den Job
    highlight_product_qrcodes_from_job(cap, product_names=["https://de.wikipedia.org", "https://softmatic.com"])

    close_window(cap)

if __name__ == "__main__":
    main()
