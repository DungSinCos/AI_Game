# ui.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
from game_logic import GameState
from ai import bfs, dfs, astar, hint

class GameUI:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)
        self.show_start()

    # ================= START SCREEN =================
    def show_start(self):
        self.clear()
        self.canvas = tk.Canvas(self.frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        bg = Image.open("assets/start.png")
        bg = bg.resize((screen_w, screen_h))
        self.start_img = ImageTk.PhotoImage(bg)
        self.canvas.create_image(0, 0, anchor="nw", image=self.start_img)

        play_btn = tk.Button(
            self.canvas,
            text="▶ CHƠI NGAY",
            font=("Arial", 18, "bold"),
            fg="darkgreen",
            bg="#f5deb3",
            activebackground="#e6c68a",
            activeforeground="darkgreen",
            relief="raised",
            bd=3,
            padx=20, pady=10,
            command=self.show_level_menu
        )
        self.canvas.create_window(screen_w // 2, screen_h - 120, window=play_btn)

    # ================= MENU LEVEL 10 + HƯỚNG DẪN =================
    def show_level_menu(self):
        self.clear()
        tk.Label(self.frame, text="CHỌN LEVEL", font=("Arial", 24, "bold")).pack(pady=20)

        self.level_num = tk.IntVar(value=1)

        # Hướng dẫn 10 level
        self.level_tips = {
            1: "Level 1: Chở cừu sang bờ phải, thuyền phải có người.",
            2: "Level 2: Không để sói và cừu một mình trên cùng bờ.",
            3: "Level 3: Không để cừu và bắp cải một mình trên cùng bờ.",
            4: "Level 4: Chỉ được chở 1 vật cùng thuyền với người.",
            5: "Level 5: Kết hợp luật Level 2 + Level 3.",
            6: "Level 6: Người phải đi thuyền trước, không được để sói trên thuyền không có người.",
            7: "Level 7: Giữ thứ tự chở sao cho không mất vật nào.",
            8: "Level 8: Tối thiểu số bước, không vi phạm luật.",
            9: "Level 9: Luật phức tạp, cần suy nghĩ kỹ trước khi chở.",
            10:"Level 10: Thách thức tối đa, chở tất cả đúng luật với ít bước nhất."
        }

        # Frame chứa các ô level
        level_frame = tk.Frame(self.frame)
        level_frame.pack(pady=10)

        # Bố trí 2 hàng × 5 cột
        colors = ["#8FBC8F","#98FB98","#00FA9A","#3CB371","#2E8B57",
                  "#20B2AA","#66CDAA","#5F9EA0","#4682B4","#1E90FF"]

        row, col = 0, 0
        for lv in range(1, 11):
            def make_start(lv=lv):
                tip = self.level_tips[lv]
                def start_level():
                    messagebox.showinfo(f"Level {lv} - Hướng dẫn", tip)
                    self.level_num.set(lv)
                    self.start_game()
                return start_level

            btn = tk.Button(
                level_frame,
                text=f"Level {lv}",
                font=("Arial", 14, "bold"),
                width=12,
                height=3,
                bg=colors[lv-1],
                fg="white",
                command=make_start(lv)
            )
            btn.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col >= 5:
                col = 0
                row += 1

    # ================= GAME =================
    def make_button(self, parent, text, fg, bg, abg, command):
        return tk.Button(
            parent,
            text=text,
            font=("Arial", 14, "bold"),
            fg=fg,
            bg=bg,
            activebackground=abg,
            activeforeground=fg,
            relief="raised",
            bd=3,
            padx=10, pady=5,
            command=command
        )

    def start_game(self):
        self.clear()
        level = self.level_num.get() if hasattr(self, "level_num") else 1
        self.state = GameState(level=level)
        self.selected = []
        self.boat_side = 0
        self.steps = 0
        self.start_time = time.time()

        screen_w = self.root.winfo_screenwidth()
        self.left_boat = int(screen_w * 0.35)
        self.right_boat = int(screen_w * 0.65)
        self.boat_x = self.left_boat

        main = tk.Frame(self.frame)
        main.pack(fill="both", expand=True)

        game_frame = tk.Frame(main)
        game_frame.pack(side="left", fill="both", expand=True)

        control = tk.Frame(main, width=260, bg="#eeeeee")
        control.pack(side="right", fill="y")

        self.canvas = tk.Canvas(game_frame)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

        tk.Label(control, text="🎮 Điều khiển", font=("Arial", 16), bg="#eeeeee").pack(pady=10)

        self.make_button(control, "🚤 Chở", "black", "#f0e68c", "#e6d96c", self.move_boat).pack(pady=5)
        self.make_button(control, "💡 Hint", "darkorange", "#ffe4b5", "#ffdead", self.use_hint).pack(pady=5)
        self.make_button(control, "🤖 BFS", "darkblue", "#add8e6", "#87ceeb", self.solve_bfs).pack(pady=5)
        self.make_button(control, "🤖 DFS", "darkred", "#f08080", "#cd5c5c", self.solve_dfs).pack(pady=5)
        self.make_button(control, "🤖 A*", "darkgreen", "#90ee90", "#66cdaa", self.solve_astar).pack(pady=5)
        self.make_button(control, "🔄 Reset", "purple", "#dda0dd", "#ba55d3", self.start_game).pack(pady=5)
        self.make_button(control, "🏠 Menu", "brown", "#f5deb3", "#e6c68a", self.show_start).pack(pady=20)

        self.info_label = tk.Label(control, text="", bg="#eeeeee", justify="left")
        self.info_label.pack(pady=20)
        self.status_label = tk.Label(control, text="", bg="#eeeeee", justify="left")
        self.status_label.pack(pady=10)

        self.load_images()
        self.draw()
        self.update_timer()

    # ================= LOAD IMAGE =================
    def load_images(self):
        def load(path, size):
            img = Image.open("assets/" + path)
            img = img.resize(size)
            return ImageTk.PhotoImage(img)

        self.images = {
            "bg": load("bg.png", (1200, 700)),
            "boat": load("boat.png", (250, 150)),
            "person": load("person.png", (100, 100)),
            "wolf": load("wolf.png", (100, 100)),
            "sheep": load("sheep.png", (100, 100)),
            "cabbage": load("cabbage.png", (100, 100)),
        }

    # ================= DRAW =================
    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_image(600, 350, image=self.images["bg"])
        self.canvas.create_image(self.boat_x, 420, image=self.images["boat"])

        screen_w = self.root.winfo_screenwidth()
        LEFT_POS = {
            "person": (int(screen_w * 0.08), 120),
            "wolf": (int(screen_w * 0.08), 250),
            "sheep": (int(screen_w * 0.08), 380),
            "cabbage": (int(screen_w * 0.08), 510)
        }
        RIGHT_POS = {
            "person": (int(screen_w * 0.8), 120),
            "wolf": (int(screen_w * 0.8), 250),
            "sheep": (int(screen_w * 0.8), 380),
            "cabbage": (int(screen_w * 0.8), 510)
        }

        for name in ["person","wolf","sheep","cabbage"]:
            idx = {"person":0,"wolf":1,"sheep":2,"cabbage":3}[name]
            side = self.state.state[idx]

            if name in self.selected:
                i = self.selected.index(name)
                slots = [(self.boat_x - 40, 380), (self.boat_x + 40, 380)]
                x, y = slots[i]
            else:
                x, y = LEFT_POS[name] if side == 0 else RIGHT_POS[name]

            self.canvas.create_image(x, y, image=self.images[name], tags=name)
            if side != self.boat_side:
                self.canvas.create_rectangle(x-40,y-40,x+40,y+40,outline="gray")
            if name in self.selected:
                self.canvas.create_rectangle(x-40,y-40,x+40,y+40,outline="red", width=2)

        self.info_label.config(
            text=f"Trạng thái:\n👨 Người: {'Phải' if self.state.state[0] else 'Trái'}\n🐺 Sói: {'Phải' if self.state.state[1] else 'Trái'}\n🐑 Cừu: {'Phải' if self.state.state[2] else 'Trái'}\n🥬 Bắp: {'Phải' if self.state.state[3] else 'Trái'}"
        )

    # ================= CLICK =================
    def on_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        tags = self.canvas.gettags(item)
        if not tags:
            return
        name = tags[0]
        idx = {"person":0,"wolf":1,"sheep":2,"cabbage":3}[name]

        if self.state.state[idx] != self.boat_side:
            return
        if name in self.selected:
            self.selected.remove(name)
        else:
            if len(self.selected) >= 2:
                return
            self.selected.append(name)
        self.draw()

    # ================= MOVE =================
    def move_boat(self, callback=None):
        if "person" not in self.selected:
            messagebox.showwarning("Lỗi", "Phải có người lái thuyền!")
            return

        target = self.right_boat if self.boat_side == 0 else self.left_boat
        step = 10 if target > self.boat_x else -10

        def animate():
            if (step > 0 and self.boat_x < target) or (step < 0 and self.boat_x > target):
                self.boat_x += step
                self.draw()
                self.root.after(20, animate)
            else:
                self.boat_x = target
                self.finish_move()
                if callback:
                    callback()
        animate()

    def finish_move(self):
        name_to_idx = {"person":0,"wolf":1,"sheep":2,"cabbage":3}
        move_idx = [name_to_idx[n] for n in self.selected]
        new_state = self.state.move(move_idx)
        if not new_state:
            messagebox.showerror("Thua", "Sai luật! Bị ăn ")
            self.selected.clear()
            self.start_game()
            return
        self.state = new_state
        self.boat_side = self.state.state[0]
        self.boat_x = self.right_boat if self.boat_side else self.left_boat
        self.selected.clear()
        self.draw()
        self.steps += 1
        self.update_status()
        if self.state.is_goal():
            messagebox.showinfo("Win", f"Bạn đã thắng Level {self.state.level}!")

    # ================= AI =================
    def use_hint(self):
        h = hint(self.state)
        if h:
            self.state = h
            self.draw()

    def solve_bfs(self):
        sol = bfs(self.state)
        if sol:
            self.animate_solution(sol)
        else:
            messagebox.showinfo("Thông báo", "AI không tìm thấy đường đi với BFS!")

    def solve_dfs(self):
        sol = dfs(self.state)
        if sol:
            self.animate_solution(sol)
        else:
            messagebox.showinfo("Thông báo", "AI không tìm thấy đường đi với DFS!")

    def solve_astar(self):
        sol = astar(self.state)
        if sol:
            self.animate_solution(sol)
        else:
            messagebox.showinfo("Thông báo", "AI không tìm thấy đường đi với A*!")

    def animate_solution(self, sol, i=1):
        if i >= len(sol):
            return
        prev = sol[i-1].state
        curr = sol[i].state
        name_to_idx = {"person":0,"wolf":1,"sheep":2,"cabbage":3}
        idx_to_name = {v:k for k,v in name_to_idx.items()}
        moved = [idx_to_name[idx] for idx in range(4) if prev[idx]!=curr[idx]]
        if "person" not in moved:
            moved.append("person")
        self.selected = moved
        def after_move():
            self.animate_solution(sol, i+1)
        self.move_boat(callback=after_move)

    # ================= TIMER & STATUS =================
    def update_timer(self):
        self.time_elapsed = int(time.time() - self.start_time)
        self.update_status()
        self.root.after(1000, self.update_timer)

    def update_status(self):
        self.status_label.config(
            text=f"⏱ Thời gian: {self.time_elapsed} giây\n🚶 Bước đi: {self.steps}"
        )

    # ================= UTIL =================
    def clear(self):
        for w in self.frame.winfo_children():
            w.destroy()
