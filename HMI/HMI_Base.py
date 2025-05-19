import tkinter as tk
from tkinter import Toplevel
import cv2
from PIL import Image, ImageTk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CV2 & GUI Oberfläche")
        self.root.state('zoomed')  # Start maximiert

        # Layout mit grid() – 3 Bereiche: video (0,0), side_buttons (0,1), bottom (1,0->1)
        self.root.grid_rowconfigure(0, weight=1)  # video und side_buttons wachsen vertikal
        self.root.grid_columnconfigure(0, weight=1)  # video wächst horizontal

        self.video_frame = tk.Frame(self.root, bg="black")
        self.video_frame.grid(row=0, column=0, sticky="nsew")

        self.side_button_frame = tk.Frame(self.root, width=200, bg="lightgray")
        self.side_button_frame.grid(row=0, column=1, sticky="ns")
        self.side_button_frame.grid_propagate(False)

        self.bottom_frame = tk.Frame(self.root, height=60, bg="gray")
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.bottom_frame.grid_propagate(False)

        self.setup_side_buttons()
        self.setup_bottom_buttons()
        self.setup_video_stream()

    def setup_side_buttons(self):
        for i in range(5):  # Beispielhaft 5 Aktionsbuttons
            btn = tk.Button(self.side_button_frame, text=f"Aktion {i+1}", width=20,
                            command=lambda i=i: self.open_action_window(i+1))
            btn.pack(pady=5, padx=10)

    def setup_bottom_buttons(self):
        tk.Button(self.bottom_frame, text="Zurück", width=15).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self.bottom_frame, text="Menü", width=15).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self.bottom_frame, text="Vor", width=15).pack(side=tk.LEFT, padx=10, pady=10)

    def open_action_window(self, index):
        win = Toplevel(self.root)
        win.title(f"Aktionsfenster {index}")
        win.geometry("400x300")
        tk.Label(win, text=f"Dies ist das Aktionsfenster {index}", font=("Arial", 16)).pack(pady=20)

    def setup_video_stream(self):
        self.cap = cv2.VideoCapture(0)
        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)

            # Dynamische Größe des video_frame
            frame_width = self.video_frame.winfo_width()
            frame_height = self.video_frame.winfo_height()
            if frame_width > 0 and frame_height > 0:
                img = img.resize((frame_width, frame_height))

            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(20, self.update_frame)

    def __del__(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
