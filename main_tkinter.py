import tkinter as tk
from tkinter import messagebox

def on_button_click():
    messagebox.showinfo("Information", "Button clicked!")

# Create the main application window
root = tk.Tk()
root.title("Beispiel Tkinter Seite")
root.geometry("400x300")

# Create a label
label = tk.Label(root, text="Willkommen zu Tkinter!", font=("Arial", 16))
label.pack(pady=20)

# Create a button
button = tk.Button(root, text="Klicken Sie mich!", command=on_button_click)
button.pack(pady=10)

# Create an entry field
entry = tk.Entry(root, width=30)
entry.pack(pady=10)

# Run the application
root.mainloop()