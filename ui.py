# ui.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
from game_logic import GameState
from ai import bfs, dfs, astar, hint, ucs, greedy
from levels import levels, IMAGE_MAP


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

        bg = Image.open("assets/start.png")
        bg.thumbnail((screen_w, screen_h), Image.Resampling.LANCZOS)
        self.start_img = ImageTk.PhotoImage(bg)

        img_x = (screen_w - self.start_img.width()) // 2
        img_y = (screen_h - self.start_img.height()) // 2
        self.canvas.create_image(img_x, img_y, anchor="nw", image=self.start_img)

        play_btn = tk.Button(
            self.canvas,
            text="▶ CHƠI NGAY",
            font=("Arial", 18, "bold"),
            fg="darkgreen",
            bg="#f5deb3",
            activebackground="#e6c68a",
            relief="raised",
            bd=3,
            padx=20, pady=10,
            command=self.show_level_menu
        )
        self.canvas.create_window(screen_w // 2, screen_h - 120, window=play_btn)

    def show_level_menu(self):
        self.clear()

        # Nền xanh
        menu_frame = tk.Frame(self.frame)
        menu_frame.pack(fill="both", expand=True)

        # Tiêu đề
        tk.Label(menu_frame, text="🌟 CHỌN LEVEL 🌟", font=("Arial", 28, "bold"),
                  fg="white").pack(pady=20)

        # Frame chứa các ô level
        levels_frame = tk.Frame(menu_frame)
        levels_frame.pack(expand=True)

        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

        total_levels = len(levels)
        for lv in range(1, total_levels + 1):
            color = colors[(lv - 1) % len(colors)]
            level_frame = tk.Frame(levels_frame, bg=color, relief="raised", bd=2, width=200, height=200)
            level_frame.grid(row=(lv - 1) // 5, column=(lv - 1) % 5, padx=20, pady=20)  # 5 cột, nhiều hàng

            tk.Label(level_frame, text=f"Level {lv}", font=("Arial", 16, "bold"),
                     bg=color, fg="white").pack(pady=10)

            def make_start(lv=lv):
                def start_level():
                    self.level_num = lv
                    self.start_game()

                return start_level

            play_btn = tk.Button(level_frame, text="🎮 CHƠI", command=make_start(),
                                 bg="black", fg="white", font=("Arial", 10, "bold"),
                                 padx=10, pady=5)
            play_btn.pack(pady=5)

        # Nút quay lại
        back_btn = tk.Button(menu_frame, text="← Quay lại", command=self.show_start,
                             font=("Arial", 12), bg="#cccccc", padx=20, pady=5)
        back_btn.pack(pady=10)

    def show_rule(self):
        level_data = levels[self.level_num]
        rule_text = level_data.get("description", "Không có luật cụ thể cho level này.")
        messagebox.showinfo("Luật chơi", rule_text)

    def start_game(self):
        self.clear()
        level = self.level_num
        level_data = levels[level]

        self.state = GameState(
            characters=level_data["characters"],
            level=level,
            boat_capacity=level_data["boat_capacity"],
            rules=level_data["rules"],
            level_data=level_data
        )

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

        # Giữ nguyên control panel rộng 260px như cũ
        control = tk.Frame(main, width=260, bg="#eeeeee")
        control.pack(side="right", fill="y")
        control.pack_propagate(False)  # Giữ kích thước cố định

        self.canvas = tk.Canvas(game_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

        # Tiêu đề
        tk.Label(control, text=f"🎮 LEVEL {level}: {level_data['name']}",
                 font=("Arial", 10, "bold"), bg="#eeeeee").pack(pady=5)

        max_items = level_data["boat_capacity"] - 1
        tk.Label(control, text=f"⛵ Sức chứa: {level_data['boat_capacity']} (tối đa {max_items} vật)",
                 font=("Arial", 9), bg="#eeeeee", fg="blue").pack(pady=5)

        self.info_label = tk.Label(control, text="", bg="#eeeeee", justify="left")
        self.info_label.pack(pady=10)
        self.status_label = tk.Label(control, text="", bg="#eeeeee", justify="left")
        self.status_label.pack(pady=10)

        # Các nút xếp dọc như cũ
        self.make_button(control, "Rule", "black", "#d3d3d3", "#c0c0c0", self.show_rule).pack(pady=5)
        self.make_button(control, "Chở", "black", "#f0e68c", "#e6d96c", self.move_boat).pack(pady=5)
        self.make_button(control, "Hint", "darkorange", "#ffe4b5", "#ffdead", self.use_hint).pack(pady=5)
        self.make_button(control, "BFS", "darkblue", "#add8e6", "#87ceeb", self.solve_bfs).pack(pady=5)
        self.make_button(control, "DFS", "darkred", "#f08080", "#cd5c5c", self.solve_dfs).pack(pady=5)
        self.make_button(control, "A*", "darkgreen", "#90ee90", "#66cdaa", self.solve_astar).pack(pady=5)
        self.make_button(control, "UCS", "darkcyan", "#e0ffff", "#afeeee", self.solve_ucs).pack(pady=5)
        self.make_button(control, "Greedy", "darkorange", "#ffebcd", "#ffdead", self.solve_greedy).pack(pady=5)
        self.make_button(control, "Reset", "purple", "#dda0dd", "#ba55d3", self.start_game).pack(pady=5)
        self.make_button(control, "Menu", "brown", "#f5deb3", "#e6c68a", self.show_start).pack(pady=10)



        self.load_images()
        self.draw()
        self.update_timer()

    def make_button(self, parent, text, fg, bg, abg, command):
        return tk.Button(
            parent,
            text=text,
            font=("Arial", 12, "bold"),
            fg=fg,
            bg=bg,
            activebackground=abg,
            activeforeground=fg,
            relief="raised",
            bd=3,
            padx=5, pady=3,
            command=command
        )

    def load_images(self):
        def load(path, size):
            img = Image.open("assets/" + path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)

        # Lấy kích thước màn hình trừ panel control (260px)
        screen_w = self.root.winfo_screenwidth() - 260
        screen_h = self.root.winfo_screenheight()

        bg_img = Image.open("assets/bg.png")
        bg_img = bg_img.resize((screen_w, screen_h), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_img)

        self.images = {
            "bg": self.bg_image,
            "boat": load("boat.png", (250, 150)),
        }

        level_data = levels[self.level_num]
        for char in level_data["characters"]:
            img_file = IMAGE_MAP.get(char, "person.png")
            self.images[char] = load(img_file, (80, 80))

    def get_display_name(self, char_name):
        """Lấy tên hiển thị có chú thích chỉ cho Level 2 và 4"""
        level_data = levels[self.level_num]

        # Chỉ hiển thị chú thích cho Level 2 và Level 4
        if self.level_num == 2:
            if char_name == "sheep1":
                return "🐑 Cừu 1 tuổi"
            elif char_name == "sheep2":
                return "🐏 Cừu 2 tuổi"
            elif char_name == "sheep3":
                return "🐏 Cừu 3 tuổi"


        elif self.level_num == 4:
            weights = level_data.get("weights", {})
            if char_name == "box_small":
                return f"📦 Thùng nhỏ ({weights.get('box_small', 30)}kg)"
            elif char_name == "box_medium":
                return f"📦 Thùng trung ({weights.get('box_medium', 60)}kg)"
            elif char_name == "box_large":
                return f"📦 Thùng lớn ({weights.get('box_large', 90)}kg)"
        return char_name

    def draw(self):
        self.canvas.delete("all")

        # Vẽ bg nhỏ ở góc trên bên trái (cách lề 10px)
        self.canvas.create_image(0, 0, anchor="nw", image=self.images["bg"])

        # Vẽ thuyền
        self.canvas.create_image(self.boat_x, 420, image=self.images["boat"])

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        characters = levels[self.level_num]["characters"]

        # Tính toán vị trí cho các nhân vật
        n_chars = len(characters)
        if n_chars <= 4:
            start_y = screen_h // 2 - 100
            y_step = 90
        else:
            start_y = screen_h // 2 - 150
            y_step = 80

        LEFT_POS = {}
        RIGHT_POS = {}

        for i, name in enumerate(characters):
            y_pos = start_y + i * y_step
            LEFT_POS[name] = (int(screen_w * 0.15), y_pos)
            RIGHT_POS[name] = (int(screen_w * 0.75), y_pos)

        for name in characters:
            idx = characters.index(name)
            side = self.state.state[idx]

            if name in self.selected:
                i = self.selected.index(name)
                num_selected = len(self.selected)
                if num_selected == 1:
                    slots = [(self.boat_x, 380)]
                elif num_selected == 2:
                    slots = [(self.boat_x - 40, 380), (self.boat_x + 40, 380)]
                else:
                    slots = [(self.boat_x - 60, 380), (self.boat_x, 380), (self.boat_x + 60, 380)]

                x, y = slots[i] if i < len(slots) else (self.boat_x, 380)
            else:
                x, y = LEFT_POS[name] if side == 0 else RIGHT_POS[name]

            # Vẽ hình ảnh
            if name in self.images:
                self.canvas.create_image(x, y, image=self.images[name], tags=name, anchor="center")

            # Vẽ chú thích bên dưới (chỉ Level 2 và 4)
            if self.level_num == 2 or self.level_num == 4:
                display_name = self.get_display_name(name)
                self.canvas.create_text(
                    x, y + 55,
                    text=display_name,
                    font=("Arial", 9, "bold"),
                    fill="white",
                    tags=f"{name}_label"
                )

            # Vẽ khung highlight
            if name in self.selected:
                self.canvas.create_rectangle(x - 45, y - 45, x + 45, y + 55, outline="red", width=3)
            elif side != self.boat_side:
                self.canvas.create_rectangle(x - 45, y - 45, x + 45, y + 55, outline="gray", width=2)

        # Cập nhật thông tin trạng thái
        info_text = "TRẠNG THÁI:\n"
        for i, name in enumerate(characters):
            side_text = " Phải" if self.state.state[i] else " Trái"
            display_name = self.get_display_name(name)
            info_text += f"{display_name}: {side_text}\n"

        max_items = self.state.boat_capacity - 1
        selected_items = [item for item in self.selected if item != "person" and item != "scientist"]
        info_text += f"Đã chọn: {len(selected_items)}/{max_items} vật"

        self.info_label.config(text=info_text)

    def on_click(self, event):
        """Xử lý click chọn vật lên thuyền"""
        item = self.canvas.find_closest(event.x, event.y)
        tags = self.canvas.gettags(item)
        if not tags:
            return
        name = tags[0]

        # Bỏ qua label tags
        if name.endswith("_label"):
            return

        characters = levels[self.level_num]["characters"]
        if name not in characters:
            return

        idx = characters.index(name)

        if self.state.state[idx] != self.boat_side:
            messagebox.showwarning("Không thể chọn", f"{self.get_display_name(name)} không ở cùng bờ với thuyền!")
            return

        selected_items = [item for item in self.selected if item != "person" and item != "scientist"]
        max_items = self.state.boat_capacity - 1

        if name in self.selected:
            self.selected.remove(name)
        else:
            if name != "person" and name != "scientist":
                if len(selected_items) >= max_items:
                    messagebox.showwarning("Quá tải", f"Thuyền chỉ chở được tối đa {max_items} vật cùng lúc!")
                    return
            self.selected.append(name)

        self.draw()

    def move_boat(self, callback=None):
        """Di chuyển thuyền"""
        characters = levels[self.level_num]["characters"]

        has_driver = False
        driver_name = None

        if "person" in characters:
            if "person" in self.selected:
                has_driver = True
                driver_name = "person"
        elif "scientist" in characters:
            if "scientist" in self.selected:
                has_driver = True
                driver_name = "scientist"

        if not has_driver:
            messagebox.showwarning("Lỗi", "Phải có người lái thuyền!")
            return

        selected_items = [item for item in self.selected if item != driver_name]
        max_items = self.state.boat_capacity - 1

        if len(selected_items) > max_items:
            messagebox.showwarning("Lỗi", f"Thuyền chỉ chở được tối đa {max_items} vật cùng lúc!")
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
        characters = levels[self.level_num]["characters"]
        name_to_idx = {name: i for i, name in enumerate(characters)}
        move_idx = [name_to_idx[n] for n in self.selected]

        new_state = self.state.move(move_idx)
        if not new_state:
            messagebox.showerror("Thua", "Sai luật! Vi phạm ràng buộc của level!")
            self.selected.clear()
            self.start_game()
            return

        self.state = new_state
        self.boat_side = self.state.state[0] if "person" in characters else self.state.state[0]
        self.boat_x = self.right_boat if self.boat_side else self.left_boat
        self.selected.clear()
        self.draw()
        self.steps += 1
        self.update_status()

        if self.state.is_goal():
            elapsed = int(time.time() - self.start_time)
            messagebox.showinfo("🎉 CHIẾN THẮNG 🎉",
                                f"Bạn đã hoàn thành Level {self.level_num}!\n"
                                f"Thời gian: {elapsed} giây\n"
                                f"Số bước: {self.steps}")
            self.show_level_menu()

    def use_hint(self):
        h = hint(self.state)
        if h:
            self.state = h
            characters = levels[self.level_num]["characters"]
            self.boat_side = self.state.state[0] if "person" in characters else self.state.state[0]
            self.boat_x = self.right_boat if self.boat_side else self.left_boat
            self.draw()
        else:
            messagebox.showinfo("Hint", "Không tìm thấy gợi ý!")

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

    def solve_ucs(self):
        sol = ucs(self.state)
        if sol:
            self.animate_solution(sol)
        else:
            messagebox.showinfo("Thông báo", "UCS không tìm thấy đường!")

    def solve_greedy(self):
        sol = greedy(self.state)
        if sol:
            self.animate_solution(sol)
        else:
            messagebox.showinfo("Thông báo", "Greedy không tìm thấy đường!")

    def solve_astar(self):
        sol = astar(self.state)
        if sol:
            self.animate_solution(sol)
        else:
            messagebox.showinfo("Thông báo", "AI không tìm thấy đường đi với A*!")

    def animate_solution(self, sol, i=1):
        if i >= len(sol):
            return
        prev = sol[i - 1].state
        curr = sol[i].state
        characters = levels[self.level_num]["characters"]
        name_to_idx = {name: i for i, name in enumerate(characters)}
        idx_to_name = {i: name for name, i in name_to_idx.items()}

        moved = [idx_to_name[idx] for idx in range(len(characters)) if prev[idx] != curr[idx]]

        if "person" in characters and "person" not in moved:
            moved.append("person")
        elif "scientist" in characters and "scientist" not in moved:
            moved.append("scientist")

        self.selected = moved

        def after_move():
            self.animate_solution(sol, i + 1)

        self.move_boat(callback=after_move)

    def update_timer(self):
        if hasattr(self, 'start_time'):
            self.time_elapsed = int(time.time() - self.start_time)
            self.update_status()
            self.root.after(1000, self.update_timer)

    def update_status(self):
        self.status_label.config(
            text=f"Thời gian: {self.time_elapsed} giây\n Số bước: {self.steps}"
        )

    def clear(self):
        for w in self.frame.winfo_children():
            w.destroy()