"""
Visualizer: interface graphique tkinter améliorée.
"""

import tkinter as tk
from tkinter import ttk
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from room import Room, MAPS, OBSTACLE, FREE, ROBOT, TARGET
from robot import Robot
from bfs_explorer import BFSExplorer
from dfs_explorer import DFSExplorer

# Palette
C_OBSTACLE  = "#1a1a2e"
C_FREE      = "#eaf0fb"
C_ROBOT     = "#2ecc71"
C_TARGET    = "#e74c3c"
C_EXPLORED  = "#5dade2"
C_PATH      = "#f4d03f"
C_ROBOT_MOV = "#1abc9c"
C_GRID      = "#c8d6e5"
C_BG        = "#0f0f1a"
C_PANEL     = "#16213e"
C_PANEL2    = "#1a1a2e"
C_TEXT      = "#e8eaf6"
C_ACCENT    = "#7c4dff"
C_BTN_RUN   = "#00b894"
C_BTN_RST   = "#636e72"
C_BTN_CMP   = "#6c5ce7"
C_BTN_STEP  = "#e17055"

CELL = 34


class Visualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Navigation Robot — BFS vs DFS")
        self.root.configure(bg=C_BG)
        self.root.resizable(True, True)

        self.room = None
        self.robot = None
        self.explorer = None
        self.current_algo = "BFS"
        self._anim_id = None
        self._explore_idx = 0
        self._step_mode = False
        self._edit_mode = False
        self._edit_val = OBSTACLE

        self._build_ui()
        self._load_map("Simple")

    # ═══════════════════════════════════════════════ BUILD UI ══
    def _build_ui(self):
        # ── Panneau gauche
        self.panel = tk.Frame(self.root, bg=C_PANEL, width=240)
        self.panel.pack(side=tk.LEFT, fill=tk.Y)
        self.panel.pack_propagate(False)

        self._section(self.panel, "🗺  Carte")
        self.map_var = tk.StringVar(value="Simple")
        cb = ttk.Combobox(self.panel, textvariable=self.map_var,
                          values=list(MAPS.keys()) + ["Aléatoire"],
                          state="readonly", width=20)
        cb.pack(padx=14, pady=(0, 10), fill=tk.X)
        cb.bind("<<ComboboxSelected>>", lambda e: self._load_map(self.map_var.get()))

        self._section(self.panel, "⚙  Algorithme")
        self.algo_var = tk.StringVar(value="BFS")
        rf = tk.Frame(self.panel, bg=C_PANEL)
        rf.pack(padx=14, pady=(0, 10), fill=tk.X)
        for algo in ("BFS", "DFS"):
            tk.Radiobutton(rf, text=algo, variable=self.algo_var, value=algo,
                           bg=C_PANEL, fg=C_TEXT, selectcolor=C_BG,
                           activebackground=C_PANEL, font=("Helvetica", 11),
                           indicatoron=0, width=7, relief=tk.FLAT,
                           bd=0, highlightthickness=0,
                           ).pack(side=tk.LEFT, padx=(0, 6))

        self._section(self.panel, "⏩  Vitesse animation")
        self.speed_var = tk.IntVar(value=50)
        spf = tk.Frame(self.panel, bg=C_PANEL)
        spf.pack(padx=14, pady=(0, 10), fill=tk.X)
        tk.Label(spf, text="Lent", bg=C_PANEL, fg="#888", font=("Helvetica", 8)).pack(side=tk.LEFT)
        tk.Scale(spf, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.speed_var,
                 bg=C_PANEL, fg=C_TEXT, troughcolor=C_BG, highlightthickness=0,
                 showvalue=False, length=120).pack(side=tk.LEFT, padx=4)
        tk.Label(spf, text="Rapide", bg=C_PANEL, fg="#888", font=("Helvetica", 8)).pack(side=tk.LEFT)

        self._section(self.panel, "✏  Édition de la carte")
        ef = tk.Frame(self.panel, bg=C_PANEL)
        ef.pack(padx=14, pady=(0, 10), fill=tk.X)
        self.edit_var = tk.BooleanVar(value=False)
        tk.Checkbutton(ef, text="Mode édition", variable=self.edit_var,
                       bg=C_PANEL, fg=C_TEXT, selectcolor=C_BG,
                       activebackground=C_PANEL, font=("Helvetica", 10),
                       command=self._toggle_edit).pack(anchor="w")
        self.edit_info = tk.Label(ef, text="Clic gauche : obstacle\nClic droit : effacer",
                                  bg=C_PANEL, fg="#888", font=("Helvetica", 8), justify=tk.LEFT)
        self.edit_info.pack(anchor="w")

        # Boutons actions
        self._section(self.panel, "▶  Actions")
        btns = [
            ("▶  Lancer",          C_BTN_RUN,  self._run),
            ("⏸  Étape par étape", C_BTN_STEP, self._step_toggle),
            ("⟳  Réinitialiser",   C_BTN_RST,  self._reset),
            ("⚖  Comparer BFS/DFS",C_BTN_CMP,  self._compare),
        ]
        for txt, bg, cmd in btns:
            tk.Button(self.panel, text=txt, command=cmd,
                      bg=bg, fg="white", font=("Helvetica", 10, "bold"),
                      relief=tk.FLAT, padx=8, pady=7, cursor="hand2",
                      activebackground=bg, bd=0).pack(fill=tk.X, padx=14, pady=3)

        # Légende
        self._section(self.panel, "🎨  Légende")
        legend = [
            (C_ROBOT,    "Départ (R)"),
            (C_TARGET,   "Cible (C)"),
            (C_OBSTACLE, "Obstacle (#)"),
            (C_FREE,     "Case libre (.)"),
            (C_EXPLORED, "Cellule explorée"),
            (C_PATH,     "Chemin solution (*)"),
            (C_ROBOT_MOV,"Robot en mouvement"),
        ]
        lf = tk.Frame(self.panel, bg=C_PANEL)
        lf.pack(padx=14, pady=(0, 10), fill=tk.X)
        for color, label in legend:
            row = tk.Frame(lf, bg=C_PANEL)
            row.pack(anchor="w", pady=1)
            tk.Label(row, bg=color, width=2, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=(0, 6))
            tk.Label(row, text=label, bg=C_PANEL, fg=C_TEXT,
                     font=("Helvetica", 9)).pack(side=tk.LEFT)

        # Stats
        self._section(self.panel, "📊  Statistiques")
        self.stat_text = tk.Text(self.panel, bg="#0a0a14", fg="#a9d18e",
                                 font=("Courier", 9), height=11,
                                 relief=tk.FLAT, state=tk.DISABLED,
                                 insertbackground=C_TEXT)
        self.stat_text.pack(padx=14, pady=(0, 10), fill=tk.X)

        # ── Zone droite
        right = tk.Frame(self.root, bg=C_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barre de statut en haut
        top_bar = tk.Frame(right, bg=C_PANEL2, pady=6)
        top_bar.pack(fill=tk.X)
        self.status_var = tk.StringVar(value="Prêt.")
        tk.Label(top_bar, textvariable=self.status_var, bg=C_PANEL2, fg=C_TEXT,
                 font=("Helvetica", 10), anchor="w", padx=12).pack(side=tk.LEFT)
        self.counter_var = tk.StringVar(value="")
        tk.Label(top_bar, textvariable=self.counter_var, bg=C_PANEL2, fg=C_PATH,
                 font=("Courier", 10, "bold"), anchor="e", padx=12).pack(side=tk.RIGHT)

        # Canvas scrollable
        canvas_container = tk.Frame(right, bg=C_BG)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_container, bg=C_BG, highlightthickness=0)
        hbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Button-3>", self._on_canvas_right_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)

    def _section(self, parent, title):
        tk.Label(parent, text=title, bg=C_PANEL, fg=C_ACCENT,
                 font=("Helvetica", 9, "bold"), anchor="w",
                 padx=14).pack(fill=tk.X, pady=(12, 2))

    # ═══════════════════════════════════════════════ CARTE ══
    def _load_map(self, name):
        self._cancel_anim()
        self._step_mode = False
        if name == "Aléatoire":
            self.room = Room(rows=13, cols=22)
        else:
            self.room = Room(grid=MAPS[name])
        self.robot = Robot(self.room.start)
        self.explorer = None
        self._draw_room()
        self._set_status(f"Carte « {name} » chargée.")
        self._clear_stats()
        self.counter_var.set("")

    def _reset(self):
        self._load_map(self.map_var.get())

    def _toggle_edit(self):
        self._edit_mode = self.edit_var.get()

    # ═══════════════════════════════════════════════ DESSIN ══
    def _draw_room(self, explored=None, path=None, robot_pos=None):
        self.canvas.delete("all")
        explored_set = set(explored or [])
        path_set = set(path or [])
        room = self.room

        for r in range(room.rows):
            for c in range(room.cols):
                x1, y1 = c * CELL, r * CELL
                x2, y2 = x1 + CELL, y1 + CELL
                cell = room.get_cell(r, c)
                pos = (r, c)

                if cell == OBSTACLE:
                    color = C_OBSTACLE
                elif pos == room.start:
                    color = C_ROBOT
                elif pos == room.target:
                    color = C_TARGET
                elif pos in path_set:
                    color = C_PATH
                elif pos in explored_set:
                    color = C_EXPLORED
                else:
                    color = C_FREE

                # Arrondi simulé avec rectangle + relief
                self.canvas.create_rectangle(
                    x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                    fill=color, outline=C_GRID, width=1
                )

                # Texte
                cx, cy = x1 + CELL // 2, y1 + CELL // 2
                if pos == room.start:
                    self.canvas.create_text(cx, cy, text="R", fill="white",
                                            font=("Helvetica", 11, "bold"))
                elif pos == room.target:
                    self.canvas.create_text(cx, cy, text="C", fill="white",
                                            font=("Helvetica", 11, "bold"))
                elif pos in path_set:
                    self.canvas.create_text(cx, cy, text="★", fill="#333",
                                            font=("Helvetica", 9))

        # Robot en mouvement
        if robot_pos and robot_pos not in (room.start, room.target):
            r, c = robot_pos
            x1, y1 = c * CELL + 5, r * CELL + 5
            x2, y2 = x1 + CELL - 10, y1 + CELL - 10
            self.canvas.create_oval(x1, y1, x2, y2,
                                    fill=C_ROBOT_MOV, outline="white", width=2)
            self.canvas.create_text(x1 + (CELL - 10) // 2, y1 + (CELL - 10) // 2,
                                    text="🤖", font=("Helvetica", 10))

        self.canvas.configure(scrollregion=(0, 0, room.cols * CELL, room.rows * CELL))

    # ═══════════════════════════════════════════════ ÉDITION ══
    def _cell_from_event(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        c, r = int(x // CELL), int(y // CELL)
        return r, c

    def _on_canvas_click(self, event):
        if not self._edit_mode:
            return
        r, c = self._cell_from_event(event)
        self._toggle_cell(r, c, OBSTACLE)

    def _on_canvas_right_click(self, event):
        if not self._edit_mode:
            return
        r, c = self._cell_from_event(event)
        self._toggle_cell(r, c, FREE)

    def _on_canvas_drag(self, event):
        if not self._edit_mode:
            return
        r, c = self._cell_from_event(event)
        self._toggle_cell(r, c, OBSTACLE)

    def _toggle_cell(self, r, c, val):
        room = self.room
        if not (0 <= r < room.rows and 0 <= c < room.cols):
            return
        if (r, c) in (room.start, room.target):
            return
        room.set_cell(r, c, val)
        self._draw_room()

    # ═══════════════════════════════════════════════ RECHERCHE ══
    def _run(self):
        self._cancel_anim()
        self._step_mode = False
        self._launch_search()

    def _step_toggle(self):
        if self.explorer is None or not self.explorer.success:
            # Lancer en mode step
            self._cancel_anim()
            self._step_mode = True
            self._launch_search(animate=False)
            self._explore_idx = 0
            self._set_status("Mode étape par étape — cliquez « Étape par étape » pour avancer.")
        else:
            # Avancer d'une étape
            self._do_step()

    def _launch_search(self, animate=True):
        algo = self.algo_var.get()
        self.current_algo = algo
        if algo == "BFS":
            self.explorer = BFSExplorer(self.room)
        else:
            self.explorer = DFSExplorer(self.room)
        self.explorer.search()
        self._explore_idx = 0
        self.robot = Robot(self.room.start)
        self.robot.set_path(self.explorer.path)

        if animate:
            self._set_status(f"Exploration {algo}...")
            self._animate_explore()

    def _do_step(self):
        exp = self.explorer
        if self._explore_idx < len(exp.explored):
            self._draw_room(explored=exp.explored[:self._explore_idx + 1])
            self.counter_var.set(f"Exploration : {self._explore_idx + 1}/{len(exp.explored)}")
            self._explore_idx += 1
        elif self.robot.move_next():
            self._draw_room(explored=exp.explored, path=exp.path,
                            robot_pos=self.robot.position())
            step = self.robot.step_index
            self.counter_var.set(f"Pas : {step}/{exp.path_length}")
        else:
            self._draw_room(explored=exp.explored, path=exp.path)
            self._set_status(f"{self.current_algo} terminé.")
            self._show_stats(exp)

    # ═══════════════════════════════════════════════ ANIMATION ══
    def _delay(self):
        # speed 1→100 : délai 200ms→5ms pour exploration, 400ms→10ms pour déplacement
        v = self.speed_var.get()
        explore_ms = int(200 - (v - 1) * (195 / 99))
        move_ms    = int(400 - (v - 1) * (390 / 99))
        return explore_ms, move_ms

    def _animate_explore(self):
        exp = self.explorer
        idx = self._explore_idx
        explore_ms, move_ms = self._delay()

        if idx < len(exp.explored):
            self._draw_room(explored=exp.explored[:idx + 1])
            self.counter_var.set(f"Exploration : {idx + 1}/{len(exp.explored)}")
            self._explore_idx += 1
            self._anim_id = self.root.after(explore_ms, self._animate_explore)
        else:
            if exp.success:
                self.robot = Robot(self.room.start)
                self.robot.set_path(exp.path)
                self._set_status(f"{self.current_algo} : chemin trouvé — animation du déplacement...")
                self._anim_id = self.root.after(move_ms, self._animate_move)
            else:
                self._draw_room(explored=exp.explored)
                self._set_status(f"{self.current_algo} : aucun chemin trouvé.")
                self._show_stats(exp)

    def _animate_move(self):
        exp = self.explorer
        _, move_ms = self._delay()
        if self.robot.move_next():
            self._draw_room(explored=exp.explored, path=exp.path,
                            robot_pos=self.robot.position())
            step = self.robot.step_index
            self.counter_var.set(f"Pas : {step}/{exp.path_length}")
            self._anim_id = self.root.after(move_ms, self._animate_move)
        else:
            self._draw_room(explored=exp.explored, path=exp.path)
            self._set_status(f"{self.current_algo} terminé. Chemin : {exp.path_length} pas.")
            self.counter_var.set(f"✅ {exp.path_length} pas")
            self._show_stats(exp)

    def _cancel_anim(self):
        if self._anim_id:
            self.root.after_cancel(self._anim_id)
            self._anim_id = None

    # ═══════════════════════════════════════════════ STATS ══
    def _show_stats(self, exp, label=None):
        algo = label or self.current_algo
        status = "✅ Succès" if exp.success else "❌ Échec"
        text = (
            f"─── {algo} ───────────────\n"
            f"Statut         : {status}\n"
            f"Nœuds explorés : {exp.nodes_explored}\n"
            f"Longueur chemin: {exp.path_length}\n"
            f"Temps (ms)     : {exp.exec_time * 1000:.3f}\n"
        )
        self._write_stats(text)

    def _write_stats(self, text, append=False):
        self.stat_text.config(state=tk.NORMAL)
        if not append:
            self.stat_text.delete("1.0", tk.END)
        self.stat_text.insert(tk.END, text)
        self.stat_text.config(state=tk.DISABLED)

    def _clear_stats(self):
        self.stat_text.config(state=tk.NORMAL)
        self.stat_text.delete("1.0", tk.END)
        self.stat_text.config(state=tk.DISABLED)

    def _set_status(self, msg):
        self.status_var.set(msg)

    # ═══════════════════════════════════════════════ COMPARAISON ══
    def _compare(self):
        self._cancel_anim()
        bfs = BFSExplorer(self.room)
        dfs = DFSExplorer(self.room)
        bfs.search()
        dfs.search()

        # Stats dans le panneau
        self.stat_text.config(state=tk.NORMAL)
        self.stat_text.delete("1.0", tk.END)
        for exp, name in [(bfs, "BFS"), (dfs, "DFS")]:
            s = "✅" if exp.success else "❌"
            self.stat_text.insert(tk.END,
                f"─── {name} ───────────────\n"
                f"Statut         : {s}\n"
                f"Nœuds explorés : {exp.nodes_explored}\n"
                f"Longueur chemin: {exp.path_length}\n"
                f"Temps (ms)     : {exp.exec_time * 1000:.3f}\n\n"
            )
        self.stat_text.config(state=tk.DISABLED)

        # Fenêtre comparaison
        win = tk.Toplevel(self.root)
        win.title("⚖  Comparaison BFS vs DFS")
        win.configure(bg=C_BG)
        win.resizable(False, False)

        headers = ["Critère", "BFS", "DFS", "Meilleur"]
        rows_data = [
            ("Nœuds explorés",
             bfs.nodes_explored, dfs.nodes_explored,
             "BFS" if bfs.nodes_explored <= dfs.nodes_explored else "DFS"),
            ("Longueur chemin",
             bfs.path_length or "—", dfs.path_length or "—",
             "BFS" if (bfs.path_length or 9999) <= (dfs.path_length or 9999) else "DFS"),
            ("Temps (ms)",
             f"{bfs.exec_time*1000:.3f}", f"{dfs.exec_time*1000:.3f}",
             "BFS" if bfs.exec_time <= dfs.exec_time else "DFS"),
            ("Chemin trouvé",
             "Oui" if bfs.success else "Non",
             "Oui" if dfs.success else "Non", "—"),
        ]

        hdr = {"bg": "#2d2d5e", "fg": C_TEXT, "font": ("Helvetica", 10, "bold"),
               "padx": 18, "pady": 10, "relief": tk.FLAT}
        cell_even = {"bg": C_PANEL,  "fg": C_TEXT, "font": ("Helvetica", 10),
                     "padx": 18, "pady": 8, "relief": tk.FLAT}
        cell_odd  = {"bg": C_PANEL2, "fg": C_TEXT, "font": ("Helvetica", 10),
                     "padx": 18, "pady": 8, "relief": tk.FLAT}

        for col, h in enumerate(headers):
            tk.Label(win, text=h, **hdr).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        for i, (crit, bv, dv, best) in enumerate(rows_data, 1):
            style = cell_even if i % 2 == 0 else cell_odd
            for col, val in enumerate([crit, bv, dv, best]):
                fg = C_PATH if col == 3 and val != "—" else C_TEXT
                tk.Label(win, text=str(val), **{**style, "fg": fg}
                         ).grid(row=i, column=col, sticky="nsew", padx=1, pady=1)

        # Conclusion
        if bfs.success and dfs.success:
            if bfs.path_length < dfs.path_length:
                conclusion = "BFS trouve le chemin le plus court."
            elif dfs.path_length < bfs.path_length:
                conclusion = "DFS trouve un chemin plus court ici."
            else:
                conclusion = "Les deux algorithmes trouvent un chemin de même longueur."
            if bfs.nodes_explored < dfs.nodes_explored:
                conclusion += "\nBFS explore moins de nœuds."
            else:
                conclusion += "\nDFS explore moins de nœuds."
        else:
            conclusion = "Un des algorithmes n'a pas trouvé de chemin."

        tk.Label(win, text=conclusion, bg=C_BG, fg="#a9d18e",
                 font=("Helvetica", 10, "italic"), padx=18, pady=12,
                 justify=tk.LEFT).grid(row=len(rows_data)+1, column=0,
                                       columnspan=4, sticky="w")

        self._set_status("Comparaison BFS/DFS effectuée.")
        self._draw_room(explored=bfs.explored, path=bfs.path)
