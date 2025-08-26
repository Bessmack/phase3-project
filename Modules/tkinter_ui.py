import tkinter as tk
from tkinter import ttk, messagebox

def tkinter_ui():
    root = tk.Tk()
    root.title("MAIN MENU")
    root.geometry("700x520")

    f_label = tk.Label(root, text="Welcome to Space Invaders!", font=("Arial", 18, "bold"))
    f_label.pack(pady=20)

    s_label = tk.Label(root, text="Enter Player's name Below")
    s_label.pack(pady=(10, 2))

    entry = tk.Entry(root, textvariable="Player 1")
    entry.pack(pady=4)
    entry.focus_set()

    btns_section = tk.Frame(root)
    btns_section.pack(pady=16)


    # Adding style for my Interface buttons
    def create_button(parent, text):
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 14, "bold"),
            bg="#A05FC6",
            activebackground="#581781",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        )

        # Add hover effect
        def on_enter(e):
            btn.config(bg="#A05FC6")
        def on_leave(e):
            btn.config(bg="#A05FC6")

        return btn

    # Create buttons
    button1 = create_button(btns_section, "Start Game")
    button1.grid(row=0, column=0, padx=10)

    button2 = create_button(btns_section, "High Scores")
    button2.grid(row=0, column=1, padx=10)

    button3 = create_button(btns_section, "Exit.")
    button3.grid(row=0, column=2, padx=10)

    root.mainloop()


tkinter_ui()








