"""
UI components (Tkinter scoreboard and Pygame menus)
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import math
from modules.database import db_get_scores, db_add_score, db_update_score, db_delete_score
from modules.config import WIDTH, HEIGHT
from modules.game import run_game

def open_scoreboard(last_result: dict = None):
    """Open the Tkinter scoreboard UI"""
    def refresh_tree():
        for i in tree.get_children():
            tree.delete(i)
        filt = mode_filter_var.get()
        filt = None if filt == "All" else filt
        for rid, player, mode, score, dur, ts in db_get_scores(filt):
            tree.insert("", tk.END, iid=str(rid), values=(rid, player, mode, score, f"{dur:.1f}", ts))

    def on_add():
        try:
            player = entry_player.get().strip() or "Player"
            mode = mode_var.get()
            score = int(entry_score.get())
            if score < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Score must be a non-negative integer.")
            return
        db_add_score(player, mode, score, 0.0)
        refresh_tree()
        entry_player.delete(0, tk.END)
        entry_score.delete(0, tk.END)

    def on_update():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select a row to update.")
            return
        rid = int(sel[0])
        player = entry_player.get().strip() or None
        mode = mode_var.get() if mode_var.get() in ("Easy", "Medium", "Hard") else None
        score_text = entry_score.get().strip()
        score_val = int(score_text) if score_text else None
        try:
            if score_val is not None and score_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Score must be a non-negative integer.")
            return
        db_update_score(rid, player=player if player else None, mode=mode, score=score_val)
        refresh_tree()

    def on_delete():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select a row to delete.")
            return
        rid = int(sel[0])
        if messagebox.askyesno("Confirm", f"Delete record #{rid}?"):
            db_delete_score(rid)
            refresh_tree()

    def on_tree_select(event=None):
        sel = tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        vals = tree.item(sel[0], 'values')
        entry_player.delete(0, tk.END)
        entry_player.insert(0, vals[1])
        entry_score.delete(0, tk.END)
        entry_score.insert(0, vals[3])
        mode_var.set(vals[2])

    def launch_from_board(mode_name: str):
        root.destroy()
        run_game(mode_name)

    root = tk.Tk()
    root.title("Space Shooter — Scores & CRUD")
    root.geometry("880x560")

    title = ttk.Label(root, text="Scores & Leaderboard", font=("Arial", 18, "bold"))
    title.pack(pady=8)

    topbar = ttk.Frame(root)
    topbar.pack(fill=tk.X, padx=10)

    ttk.Label(topbar, text="Filter by mode:").pack(side=tk.LEFT)
    mode_filter_var = tk.StringVar(value="All")
    mode_filter = ttk.Combobox(topbar, textvariable=mode_filter_var, values=["All", "Easy", "Medium", "Hard"], width=10, state="readonly")
    mode_filter.pack(side=tk.LEFT, padx=6)
    mode_filter.bind("<<ComboboxSelected>>", lambda e: refresh_tree())

    btns = ttk.Frame(topbar)
    btns.pack(side=tk.RIGHT)
    ttk.Button(btns, text="Start Easy", command=lambda: launch_from_board("Easy")).pack(side=tk.LEFT, padx=4)
    ttk.Button(btns, text="Start Medium", command=lambda: launch_from_board("Medium")).pack(side=tk.LEFT, padx=4)
    ttk.Button(btns, text="Start Hard", command=lambda: launch_from_board("Hard")).pack(side=tk.LEFT, padx=4)

    cols = ("id", "player", "mode", "score", "duration_sec", "played_at")
    tree = ttk.Treeview(root, columns=cols, show="headings", height=16)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor=tk.CENTER, stretch=True, width=100)
    tree.column("player", width=150)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    form = ttk.Frame(root)
    form.pack(fill=tk.X, padx=10, pady=4)

    ttk.Label(form, text="Player:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
    entry_player = ttk.Entry(form)
    entry_player.grid(row=0, column=1, padx=4, pady=4)

    ttk.Label(form, text="Mode:").grid(row=0, column=2, sticky=tk.W, padx=4, pady=4)
    mode_var = tk.StringVar(value="Easy")
    cmb = ttk.Combobox(form, textvariable=mode_var, values=["Easy", "Medium", "Hard"], state="readonly", width=10)
    cmb.grid(row=0, column=3, padx=4, pady=4)

    ttk.Label(form, text="Score:").grid(row=0, column=4, sticky=tk.W, padx=4, pady=4)
    entry_score = ttk.Entry(form, width=10)
    entry_score.grid(row=0, column=5, padx=4, pady=4)

    actions = ttk.Frame(root)
    actions.pack(pady=6)
    ttk.Button(actions, text="Add", command=on_add).pack(side=tk.LEFT, padx=6)
    ttk.Button(actions, text="Update Selected", command=on_update).pack(side=tk.LEFT, padx=6)
    ttk.Button(actions, text="Delete Selected", command=on_delete).pack(side=tk.LEFT, padx=6)
    ttk.Button(actions, text="Close", command=root.destroy).pack(side=tk.LEFT, padx=6)

    refresh_tree()

    if last_result:
        banner = ttk.Label(root, foreground="#0a0", font=("Arial", 12, "bold"),
                           text=f"Last game — {last_result['mode']} | Player: {last_result['player']} | Score: {last_result['score']} | Duration: {last_result['duration_sec']:.1f}s")
        banner.pack(pady=4)

    root.mainloop()

def launcher_menu(screen, clock, bigfont):
    """Display the Pygame launcher menu"""
    running = True
    frame = 0
    buttons = []
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for label, rect in buttons:
                    if rect.collidepoint(mx, my):
                        return label

        screen.fill((6, 6, 20))
        for i in range(70):
            x = (i * 31 + frame * 2) % WIDTH
            y = (i * 13 + int(math.sin((frame + i) * 0.05) * 50)) % HEIGHT
            pygame.draw.circle(screen, (200, 200, 255), (x, y), 2)

        title = bigfont.render("SPACE SHOOTER", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        bw, bh = 240, 70
        by = 220
        gap = 20
        labels = ["Easy", "Medium", "Hard"]
        buttons = []
        for idx, lbl in enumerate(labels):
            rect = pygame.Rect(WIDTH // 2 - bw // 2, by + idx * (bh + gap), bw, bh)
            buttons.append((lbl, rect))
            color = (40, 140, 255) if idx == 0 else (80, 200, 120) if idx == 1 else (220, 80, 220)
            pygame.draw.rect(screen, color, rect, border_radius=16)
            txt = bigfont.render(lbl, True, (15, 15, 25))
            screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        footer = pygame.font.SysFont("arial", 18).render(
            "Click a mode to start. After the game, a Tkinter scoreboard opens.",
            True, (210, 210, 210)
        )
        screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 60))

        pygame.display.flip()
        clock.tick(60)
        frame += 1
