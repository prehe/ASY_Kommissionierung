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
    
    job_products = {
        "124343433": ["Platine 234", "Platine 376"],
        "192343324": ["Platine 123"]
    }

    job_id = scan_new_job(cap)
    print(f"Neuer Job-ID: {job_id}")
    # Warte auf QR-Code-Scan für den Job
    highlight_product_qrcodes_from_job(cap, product_names=job_products[job_id])

    close_window(cap)

if __name__ == "__main__":
    main()
