import tkinter as tk
import time
from tkinter import messagebox
from PIL import Image, ImageTk
from game_logic import GameState
from ai import bfs, hint, dfs, astar

class GameUI:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)
        self.show_start()


    def show_start(self):
        self.clear()
        self.canvas = tk.Canvas(self.frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # ảnh nền
        bg = Image.open("assets/start.png")
        bg = bg.resize((screen_w, screen_h))
        self.start_img = ImageTk.PhotoImage(bg)
        self.canvas.create_image(0, 0, anchor="nw", image=self.start_img)

        # tạo nút bằng code (khối màu + chữ)
        play_btn = tk.Button(
            self.canvas,
            text="▶ CHƠI NGAY",
            font=("Arial", 18, "bold"),
            fg="darkgreen",
            bg="#f5deb3",  # màu be
            activebackground="#e6c68a",  # màu khi hover
            activeforeground="darkgreen",
            relief="raised",
            bd=3,
            padx=20, pady=10,
            command=self.show_level_menu
        )

        # đặt nút vào giữa dưới màn hình
        self.canvas.create_window(screen_w // 2, screen_h - 120, window=play_btn)

    def on_start_click(self, event):
        x, y = event.x, event.y
        x1, y1, x2, y2 = self.play_btn_area
        if x1 <= x <= x2 and y1 <= y <= y2:
            self.show_level_menu()

    # ================= MENU =================
    def show_level_menu(self):
        self.clear()
        tk.Label(self.frame, text="Chọn Level", font=("Arial", 18)).pack(pady=20)

        self.level = tk.StringVar(value="Dễ")
        for lv in ["Dễ", "Trung bình", "Khó"]:
            tk.Radiobutton(self.frame, text=lv, variable=self.level, value=lv).pack(pady=5)
        tk.Button(self.frame, text="▶ Bắt đầu", command=self.start_game).pack(pady=20)

    # ================= GAME =================
    def start_game(self):
        self.clear()
        self.state = GameState()
        self.selected = []
        self.boat_side = 0

        # reset bước đi và thời gian
        self.steps = 0
        self.start_time = time.time()  # lưu thời điểm bắt đầu

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # vị trí thuyền
        self.left_boat = int(screen_w * 0.35)
        self.right_boat = int(screen_w * 0.65)
        self.boat_x = self.left_boat

        # ===== layout 2 cột =====
        main = tk.Frame(self.frame)
        main.pack(fill="both", expand=True)

        game_frame = tk.Frame(main)
        game_frame.pack(side="left", fill="both", expand=True)

        control = tk.Frame(main, width=260, bg="#eeeeee")
        control.pack(side="right", fill="y")

        # canvas
        self.canvas = tk.Canvas(game_frame)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

        # panel phải
        tk.Label(control, text="🎮 Điều khiển", font=("Arial", 16), bg="#eeeeee").pack(pady=10)

        tk.Button(control, text="🚤 Chở", width=15, command=self.move_boat).pack(pady=5)
        tk.Button(control, text="💡 Hint", width=15, command=self.use_hint).pack(pady=5)
        # Trong start_game, thay vì nút Solve:
        tk.Button(control, text="🤖 BFS", width=15, command=self.solve_bfs).pack(pady=5)
        tk.Button(control, text="🤖 DFS", width=15, command=self.solve_dfs).pack(pady=5)
        tk.Button(control, text="🤖 A*", width=15, command=self.solve_astar).pack(pady=5)

        tk.Button(control, text="🔄 Reset", width=15, command=self.start_game).pack(pady=5)
        tk.Button(control, text="🏠 Menu", width=15, command=self.show_start).pack(pady=20)

        self.info_label = tk.Label(control, text="", bg="#eeeeee", justify="left")
        self.info_label.pack(pady=20)

        # thêm label hiển thị thời gian và bước đi
        self.status_label = tk.Label(control, text="", bg="#eeeeee", justify="left")
        self.status_label.pack(pady=10)

        self.load_images()
        self.draw()

        # bắt đầu đếm thời gian
        self.update_timer()

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

    # ================= TIMER & STATUS =================
    def update_timer(self):
        # tính số giây đã trôi qua
        elapsed = int(time.time() - self.start_time)
        self.time_elapsed = elapsed
        self.update_status()
        self.root.after(1000, self.update_timer)

    def update_status(self):
        self.status_label.config(
            text=f"⏱ Thời gian: {self.time_elapsed} giây\n"
                 f"🚶 Bước đi: {self.steps}"
        )

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
                slots = [
                    (self.boat_x - 40, 380),
                    (self.boat_x + 40, 380)
                ]
                x, y = slots[i]
            else:
                x, y = LEFT_POS[name] if side == 0 else RIGHT_POS[name]

            self.canvas.create_image(x, y, image=self.images[name], tags=name)

            if side != self.boat_side:
                self.canvas.create_rectangle(x-40,y-40,x+40,y+40,outline="gray")

            if name in self.selected:
                self.canvas.create_rectangle(x-40,y-40,x+40,y+40,outline="red", width=2)

        # info
        self.info_label.config(
            text=f"Trạng thái:\n"
                 f"👨 Người: {'Phải' if self.state.state[0] else 'Trái'}\n"
                 f"🐺 Sói: {'Phải' if self.state.state[1] else 'Trái'}\n"
                 f"🐑 Cừu: {'Phải' if self.state.state[2] else 'Trái'}\n"
                 f"🥬 Bắp: {'Phải' if self.state.state[3] else 'Trái'}"
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
        name_to_idx = {
            "person": 0,
            "wolf": 1,
            "sheep": 2,
            "cabbage": 3
        }

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

        # tăng số bước đi
        self.steps += 1
        self.update_status()

        if self.state.is_goal():
            messagebox.showinfo("Win", "Bạn đã thắng!")

    # ================= AI =================
    def use_hint(self):
        h = hint(self.state)
        if h:
            self.state = h
            self.draw()
    #HÀM SOLVE
    def solve(self):
        algo_type = self.algo.get() 
        sol = None
        # 2. Kiểm tra và gọi đúng hàm AI tương ứng
        if algo_type == "BFS":
            sol = bfs(self.state)
        elif algo_type == "DFS":
            sol = dfs(self.state) # Phải gọi đúng tên hàm Duy viết trong ai.py
        elif algo_type == "A*":
            sol = astar(self.state)
        
        # 3. Nếu tìm thấy lời giải thì chạy hiệu ứng di chuyển
        if sol:
            self.animate_solution(sol)
        else:
            messagebox.showinfo("Thông báo", "AI không tìm thấy đường đi!")

    def animate_solution(self, sol, i=1):
        # i=1 vì sol[0] là trạng thái ban đầu
        if i >= len(sol):
            return

        # tìm nhân vật nào thay đổi vị trí giữa sol[i-1] và sol[i]
        prev = sol[i - 1].state
        curr = sol[i].state
        name_to_idx = {"person": 0, "wolf": 1, "sheep": 2, "cabbage": 3}
        idx_to_name = {v: k for k, v in name_to_idx.items()}

        moved = []
        for idx in range(4):
            if prev[idx] != curr[idx]:
                moved.append(idx_to_name[idx])

        # gán selected để move_boat biết ai đang trên thuyền
        self.selected = moved

        # sau khi thuyền chạy xong thì gọi tiếp animate_solution cho bước kế
        def after_move():
            self.animate_solution(sol, i + 1)

        # sửa move_boat để nhận callback khi xong
        self.move_boat(callback=after_move)

    # ================= UTIL =================
    def clear(self):
        for w in self.frame.winfo_children():
            w.destroy()
