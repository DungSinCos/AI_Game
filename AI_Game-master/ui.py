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
                 fg="black").pack(pady=20)

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
                     bg=color, fg="black").pack(pady=10)

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

        # Thêm thông tin bổ sung cho từng level
        if self.level_num == 2:
            rule_text += "\n\n📋 Luật cụ thể:\n- Thuyền chở: 1 người + tối đa 2 cừu\n- Cừu hơn kém nhau 1 tuổi (1-2 hoặc 2-3) KHÔNG được ở cùng nhau nếu không có người\n- Cừu 1 và 3 tuổi có thể ở cùng nhau vì chênh lệch 2 tuổi"
        elif self.level_num == 3:
            time_limit = level_data.get("time_limit", 60)
            rule_text += f"\n\n⏱️ Thời gian giới hạn: {time_limit} giây\n⚠️ Bom phải luôn có nhà nghiên cứu giám sát!"
        elif self.level_num == 4:
            weight_limit = level_data.get("weight_limit", 100)
            weights = level_data.get("weights", {})
            rule_text += f"\n\n📊 Thông tin thêm:\n- Giới hạn trọng lượng: {weight_limit}kg\n- Thùng nhỏ: {weights.get('box_small', 30)}kg\n- Thùng trung: {weights.get('box_medium', 60)}kg\n- Thùng lớn: {weights.get('box_large', 90)}kg\n- Thùng nhỏ và thùng vừa không được ở cùng nhau\n- Thùng lớn và thùng nhỏ không được ở cùng nhau"
        elif self.level_num == 5:
            tiger_times = level_data.get("tiger_times", {})
            time_limit = level_data.get("time_limit", 30)
            rule_text += f"\n\n⏱️ Thông tin thêm:\n- Giới hạn thời gian: {time_limit} giây\n- Hổ nhanh (tiger1): {tiger_times.get('tiger1', 1)} giây\n- Hổ trung bình 1 (tiger2): {tiger_times.get('tiger2', 3)} giây\n- Hổ trung bình 2 (tiger3): {tiger_times.get('tiger3', 6)} giây\n- Hổ chậm (tiger4): {tiger_times.get('tiger4', 8)} giây\n- Hổ rất chậm (tiger5): {tiger_times.get('tiger5', 12)} giây\n\nMỗi lần thuyền qua sông mất thời gian = thời gian của con hổ chậm nhất trên thuyền.\nHổ nhanh (1s,3s) và hổ chậm (8s,12s) không được ở cùng nhau nếu không có hổ 6s."

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
        self.time_elapsed = 0
        self.game_over = False

        # Thêm biến để theo dõi số lượt còn lại cho level 7
        if level == 7:
            self.move_limit = level_data.get("move_limit", 5)
            self.remaining_moves = self.move_limit

        screen_w = self.root.winfo_screenwidth()
        self.left_boat = int(screen_w * 0.35)
        self.right_boat = int(screen_w * 0.55)
        self.boat_x = self.left_boat

        main = tk.Frame(self.frame)
        main.pack(fill="both", expand=True)

        game_frame = tk.Frame(main)
        game_frame.pack(side="left", fill="both", expand=True)

        # Giữ nguyên control panel rộng 260px như cũ
        control = tk.Frame(main, width=260, bg="#eeeeee")
        control.pack(side="right", fill="y")
        control.pack_propagate(False)

        self.canvas = tk.Canvas(game_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

        # Tiêu đề
        tk.Label(control, text=f"🎮 LEVEL {level}: {level_data['name']}",
                 font=("Arial", 10, "bold"), bg="#eeeeee").pack(pady=5)

        max_items = level_data["boat_capacity"] - 1
        tk.Label(control, text=f"⛵ Sức chứa: {level_data['boat_capacity']} (tối đa {max_items} vật)",
                 font=("Arial", 9), bg="#eeeeee", fg="blue").pack(pady=5)

        if level == 2:
            tk.Label(control, text=f"🐑 Luật: Cừu chênh lệch 1 tuổi không ở cùng nhau nếu không có người",
                     font=("Arial", 8), bg="#eeeeee", fg="red", wraplength=240).pack(pady=2)
        elif level == 3:
            time_limit = level_data.get("time_limit", 60)
            tk.Label(control, text=f"⏱️ Thời gian giới hạn: {time_limit} giây",
                     font=("Arial", 9), bg="#eeeeee", fg="green").pack(pady=2)
            tk.Label(control, text=f"⚠️ Bom phải có nhà nghiên cứu giám sát",
                     font=("Arial", 8), bg="#eeeeee", fg="red", wraplength=240).pack(pady=2)
        elif level == 4:
            weight_limit = level_data.get("weight_limit", 100)
            tk.Label(control, text=f"⚖️ Giới hạn trọng lượng: {weight_limit}kg",
                     font=("Arial", 9), bg="#eeeeee", fg="green").pack(pady=2)
        elif level == 5:
            time_limit = level_data.get("time_limit", 30)
            tk.Label(control, text=f"⏱️ Tối ưu thời gian (≤{time_limit}s)",
                     font=("Arial", 9), bg="#eeeeee", fg="green").pack(pady=2)
        elif level == 7:
            move_limit = level_data.get("move_limit", 5)
            tk.Label(control, text=f"💣 Bom sẽ nổ sau {move_limit} lượt",
                     font=("Arial", 9), bg="#eeeeee", fg="red").pack(pady=2)

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

    def update_timer(self):
        if hasattr(self, 'start_time'):
            self.time_elapsed = int(time.time() - self.start_time)
            self.update_status()
            self.root.after(1000, self.update_timer)

    def make_button(self, parent, text, fg, bg, abg, command):
        return tk.Button(
            parent,
            text=text,
            font=("Arial", 10, "bold"),
            fg=fg,
            bg=bg,
            activebackground=abg,
            activeforeground=fg,
            relief="raised",
            bd=3,
            padx=3, pady=3,
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
        """Lấy tên hiển thị có chú thích"""
        level_data = levels[self.level_num]

        # Level 2: Hiển thị tuổi cừu
        if self.level_num == 2:
            if char_name == "sheep1":
                return "🐑 Cừu 1 tuổi"
            elif char_name == "sheep2":
                return "🐏 Cừu 2 tuổi"
            elif char_name == "sheep3":
                return "🐏 Cừu 3 tuổi"

        # Level 4: Hiển thị trọng lượng thùng
        elif self.level_num == 4:
            weights = level_data.get("weights", {})
            if char_name == "box_small":
                return f"📦 Thùng nhỏ ({weights.get('box_small', 30)}kg)"
            elif char_name == "box_medium":
                return f"📦 Thùng trung ({weights.get('box_medium', 60)}kg)"
            elif char_name == "box_large":
                return f"📦 Thùng lớn ({weights.get('box_large', 90)}kg)"

        # Level 5: Hiển thị tên và thời gian của hổ
        elif self.level_num == 5:
            tiger_times = level_data.get("tiger_times", {})
            if char_name in tiger_times:
                time_val = tiger_times[char_name]
                # Đặt tên hiển thị cho từng con hổ
                if char_name == "tiger1":
                    return f"🐯 Hổ nhanh ({time_val}s)"
                elif char_name == "tiger2":
                    return f"🐯 Hổ trung bình 1 ({time_val}s)"
                elif char_name == "tiger3":
                    return f"🐯 Hổ trung bình 2 ({time_val}s)"
                elif char_name == "tiger4":
                    return f"🐯 Hổ chậm ({time_val}s)"
                elif char_name == "tiger5":
                    return f"🐯 Hổ rất chậm ({time_val}s)"

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
            start_y = screen_h // 2 - 200
            y_step = 90
        elif n_chars <= 7:
            start_y = screen_h // 2 - 250
            y_step = 80
        else:
            start_y = screen_h // 2 - 300
            y_step = 70

        LEFT_POS = {}
        RIGHT_POS = {}

        for i, name in enumerate(characters):
            y_pos = start_y + i * y_step
            LEFT_POS[name] = (int(screen_w * 0.05), y_pos)
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

            # Vẽ chú thích bên dưới cho Level 2, 4, 5
            if self.level_num in [2, 4, 5]:
                display_name = self.get_display_name(name)
                # Điều chỉnh vị trí text dựa trên chiều dài tên
                text_y_offset = 55
                if self.level_num == 5 and len(display_name) > 15:
                    text_y_offset = 65
                self.canvas.create_text(
                    x, y + text_y_offset,
                    text=display_name,
                    font=("Arial", 8, "bold"),
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
        # Nếu game đã kết thúc, không cho di chuyển tiếp
        if hasattr(self, 'game_over') and self.game_over:
            return

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

        if self.level_num == 7:
            bomb_idx = self.state.characters.index("bomb")
            if self.state.state[bomb_idx] == 0:  # Bomb chưa qua sông
                self.remaining_moves = max(0, self.move_limit - self.state.moves)
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

    def show_ai_result(self, algo_name, exec_time, explored):
        """Hiển thị bảng thống kê kết quả giải thuật"""
        res_msg = (f"--- THỐNG KÊ GIẢI THUẬT ---\n"
                   f"🤖 Thuật toán: {algo_name}\n"
                   f"⏱️ Thời gian giải: {exec_time:.6f} giây\n"
                   f"🧩 Số trạng thái đã duyệt: {explored}\n"
                   f"---------------------------")
        messagebox.showinfo("Kết quả AI", res_msg)

    def run_solve(self, algo_func, name):
        """Hàm dùng chung để chạy AI và hiển thị kết quả"""
        try:
            sol, t, nodes = algo_func(self.state)
            if sol:
                self.show_ai_result(name, t, nodes)
                self.animate_solution(sol)
            else:
                messagebox.showwarning("Thông báo", f"{name} không tìm thấy lời giải!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thực thi {name}: {e}")

    # Các hàm gọi từ Button trên giao diện
    def solve_bfs(self): self.run_solve(bfs, "BFS")
    def solve_dfs(self): self.run_solve(dfs, "DFS")
    def solve_ucs(self): self.run_solve(ucs, "UCS")
    def solve_greedy(self): self.run_solve(greedy, "Greedy")
    def solve_astar(self): self.run_solve(astar, "A*")

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

    def update_status(self):
        """Cập nhật trạng thái hiển thị (thời gian, số bước)"""
        # Nếu game đã kết thúc, không cần cập nhật nữa
        if hasattr(self, 'game_over') and self.game_over:
            return

        if self.level_num == 3:
            # Level 3: Hiển thị thời gian đã qua và thời gian còn lại
            time_limit = levels[self.level_num].get("time_limit", 60)
            time_left = max(0, time_limit - self.time_elapsed)
            status_text = f"⏱️ Thời gian: {self.time_elapsed} giây\n⏰ Còn lại: {time_left} giây\n📊 Số bước: {self.steps}"

            # Kiểm tra hết giờ - chỉ thông báo một lần
            if self.time_elapsed >= time_limit and not self.state.is_goal() and not self.game_over:
                self.game_over = True
                messagebox.showinfo("Thất bại", f"Hết giờ! Bạn đã thua Level {self.level_num}!")
                self.show_level_menu()
                return

        elif self.level_num == 5:
            # Level 5: Hiển thị tổng thời gian di chuyển
            status_text = f"⏱️ Thời gian thực: {self.time_elapsed} giây\n🐯 Tổng thời gian di chuyển: {self.state.cost} giây\n📊 Số bước: {self.steps}"

            # Kiểm tra nếu tổng thời gian di chuyển vượt quá giới hạn
            time_limit = levels[self.level_num].get("time_limit", 30)
            if self.state.cost > time_limit and not self.state.is_goal() and not self.game_over:
                self.game_over = True
                messagebox.showinfo("Thất bại",
                                    f"Tổng thời gian di chuyển {self.state.cost} giây vượt quá giới hạn {time_limit} giây!")
                self.show_level_menu()
                return

        elif self.level_num == 7:
            # Level 7: Hiển thị số lượt còn lại
            # Tìm vị trí của bomb
            bomb_idx = self.state.characters.index("bomb")
            bomb_side = self.state.state[bomb_idx]

            # Nếu bomb chưa qua sông (bờ trái), tính số lượt còn lại
            if bomb_side == 0:
                remaining = max(0, self.move_limit - self.state.moves)
                status_text = f"💣 Bom ở bờ trái\n⏰ Số lượt còn lại: {remaining}/{self.move_limit}\n📊 Số bước: {self.steps}"

                # Kiểm tra nếu hết lượt và bomb chưa qua sông
                if self.state.moves >= self.move_limit and not self.state.is_goal() and not self.game_over:
                    self.game_over = True
                    messagebox.showinfo("Thất bại", f"Bom đã nổ! Bạn đã thua Level {self.level_num}!")
                    self.show_level_menu()
                    return
            else:
                # Bomb đã qua sông, hiển thị bình thường
                status_text = f"💣 Bom đã qua sông an toàn\n📊 Số bước: {self.steps}"

        else:
            # Các level khác
            status_text = f"⏱️ Thời gian: {self.time_elapsed} giây\n📊 Số bước: {self.steps}"

        self.status_label.config(text=status_text)

    def clear(self):
        for w in self.frame.winfo_children():
            w.destroy()