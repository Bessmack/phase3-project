import tkinter as tk

def tkinter_ui():
    root = tk.Tk()
    root.title("MAIN MENU")
    root.geometry("600x420")

    f_label = tk.Label(root, text="Welcome to Space Invaders!", font=("Arial", 18, "bold"))
    f_label.pack(pady=20)
    
    s_label = tk.Label(root, text="Enter Player's name Below")
    s_label.pack(pady=(10, 2))

    root.mainloop()


tkinter_ui()








