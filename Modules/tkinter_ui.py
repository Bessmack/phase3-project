import tkinter as tk
from tkinter import ttk, messagebox
from game_database import get_highest_score

def tkinter_ui():
    selected_name = {"value": None}
    root = tk.Tk()
    root.title("MAIN MENU")
    root.geometry("700x520")

    f_label = tk.Label(root, text="Welcome to Space Invaders!", font=("Arial", 18, "bold"))
    f_label.pack(pady=20)

    s_label = tk.Label(root, text="Enter Player's name Below")
    s_label.pack(pady=(10, 2))

    default_name = tk.StringVar(value="Player 1")
    entry = tk.Entry(root, textvariable=default_name)
    entry.pack(pady=4)
    entry.focus_set()

    btns_section = tk.Frame(root)
    btns_section.pack(pady=16)

    def start_game():
        name = default_name.get().strip()
        if not name:
            messagebox.showwarning("Name required", "Input A valid Name")
            return
        selected_name["value"] = name
        root.destroy()

    def show_scores_window(parent):
        window = tk.Toplevel(parent)
        window.title("High Scores")
        window.geometry("700x520")

        cols = ("Player", "Score", "When")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for p, s, when in get_highest_score(20):
            tree.insert("", tk.END, values=(p, s, when))

        ttk.Button(window, text="Close", command=window.destroy).pack(pady=6)


    # Adding style for my Interface buttons
    def create_button(holder, text, command):
        btn = tk.Button(
            holder,
            command=command,
            text=text,
            font=("Arial", 14, "bold"),
            bg="#A05FC6",
            activebackground="#581781",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        )

        return btn

    # Create buttons
    button1 = create_button(btns_section, "Start Game", start_game)
    button1.grid(row=0, column=0, padx=10)

    button2 = create_button(btns_section, "High Scores", lambda:show_scores_window(root))
    button2.grid(row=1, column=1, padx=10)

    button3 = create_button(btns_section, "Exit.", root.destroy)
    button3.grid(row=2, column=2, padx=10)

    root.mainloop()
