import tkinter as tk
from tkinter import messagebox,ttk
from PIL import Image, ImageTk
import time
from game_logic import GameState
from ai import bfs, dfs, astar, hint, ucs, greedy
from levels import levels, IMAGE_MAP
from History import history_manager



class GameUI:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)
        self.history_manager = history_manager
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

        # Hiển thị thông tin nhóm
        group_info = [
            "NHÓM THỰC HIỆN: 03",
            "Phạm Quốc Duy - 24133008",
            "Lục Long Trí Dũng - 24133010",
            "Nguyễn Thị Hoa - 24133018"
        ]

        #  (góc dưới bên phải)
        start_y = screen_h - 140
        for i, text in enumerate(group_info):
            self.canvas.create_text(
                screen_w - 20, start_y + i * 25,
                text=text,
                font=("Arial", 12, "bold"),
                fill="white",
                anchor="se",
                tags="group_info"
            )

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


        menu_frame = tk.Frame(self.frame, bg="#90EE90")  # Màu xanh lá nhẹ
        menu_frame.pack(fill="both", expand=True)
        tk.Label(menu_frame, text="🌟 CHỌN LEVEL 🌟", font=("Arial", 28, "bold"),
                 fg="black", bg="#90EE90").pack(pady=30)


        levels_frame = tk.Frame(menu_frame, bg="#90EE90")
        levels_frame.pack(expand=True)

        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
                  "#FF9F4A", "#DDA0DD", "#98D8C8", "#F7D794", "#C7CEE6"]
        total_levels = len(levels)
        rows = 2
        cols = 5

        box_width = 180
        box_height = 180

        for lv in range(1, total_levels + 1):
            row = (lv - 1) // cols
            col = (lv - 1) % cols
            if row >= rows:
                break

            color = colors[(lv - 1) % len(colors)]
            level_frame = tk.Frame(levels_frame, bg=color, relief="raised", bd=3,
                                   width=box_width, height=box_height)
            level_frame.grid(row=row, column=col, padx=20, pady=20)
            level_frame.grid_propagate(False)  # Giữ kích thước cố định

            # Level number - chữ màu đen
            tk.Label(level_frame, text=f"Level {lv}", font=("Arial", 18, "bold"),
                     bg=color, fg="black").pack(pady=30)

            def make_start(lv=lv):
                def start_level():
                    self.level_num = lv
                    self.start_game()

                return start_level

            # Nút CHƠI - chữ màu đen
            play_btn = tk.Button(level_frame, text="🎮 CHƠI", command=make_start(),
                                 bg="white", fg="black", font=("Arial", 12, "bold"),
                                 padx=15, pady=8, bd=0, cursor="hand2")
            play_btn.pack(pady=10)

        # Nút quay lại - chữ màu đen
        button_frame = tk.Frame(menu_frame, bg="#90EE90")
        button_frame.pack(pady=25)

        back_btn = tk.Button(button_frame, text="← Quay lại", command=self.show_start,
                             font=("Arial", 14, "bold"), bg="#F4A460", fg="black",
                             padx=25, pady=10, bd=0, cursor="hand2")
        back_btn.pack(side="left", padx=10)

        # Thêm nút xem lịch sử
        history_btn = tk.Button(button_frame, text="📜 Xem lịch sử", command=self.show_history,
                                font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                                padx=25, pady=10, bd=0, cursor="hand2")
        history_btn.pack(side="left", padx=10)

    def show_history(self):
        """Hiển thị cửa sổ lịch sử chạy thuật toán với chức năng reset và sắp xếp"""
        import tkinter as tk
        from tkinter import ttk

        history_window = tk.Toplevel(self.root)
        history_window.title("Lịch sử chạy thuật toán")
        history_window.geometry("1000x650")
        history_window.configure(bg="#f0f0f0")

        # Center window
        history_window.update_idletasks()
        x = (history_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (history_window.winfo_screenheight() // 2) - (650 // 2)
        history_window.geometry(f"1000x650+{x}+{y}")

        # Frame chính
        main_frame = tk.Frame(history_window, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tiêu đề
        tk.Label(main_frame, text="📊 LỊCH SỬ CHẠY THUẬT TOÁN",
                 font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#333").pack(pady=10)

        # Frame lọc và sắp xếp
        filter_frame = tk.Frame(main_frame, bg="#f0f0f0")
        filter_frame.pack(fill="x", pady=5)

        # Lọc theo Level
        tk.Label(filter_frame, text="Lọc theo Level:", bg="#f0f0f0").pack(side="left", padx=5)
        level_var = tk.StringVar(value="Tất cả")
        level_combo = ttk.Combobox(filter_frame, textvariable=level_var,
                                   values=["Tất cả"] + list(range(1, 11)),
                                   width=10, state="readonly")
        level_combo.pack(side="left", padx=5)

        # Lọc theo Thuật toán
        tk.Label(filter_frame, text="Thuật toán:", bg="#f0f0f0").pack(side="left", padx=5)
        algo_var = tk.StringVar(value="Tất cả")
        algo_combo = ttk.Combobox(filter_frame, textvariable=algo_var,
                                  values=["Tất cả", "BFS", "DFS", "UCS", "Greedy", "A*"],
                                  width=10, state="readonly")
        algo_combo.pack(side="left", padx=5)

        # Frame chứa Treeview và Scrollbar
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, pady=10)

        # Tạo scrollbar
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        # Tạo Treeview
        columns = ("ID", "Thời gian", "Level", "Tên Level", "Thuật toán",
                   "Thời gian chạy", "Số trạng thái", "Số bước", "Chi phí")

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                            yscrollcommand=scrollbar.set, height=20)
        scrollbar.config(command=tree.yview)

        # Định nghĩa các cột
        for col in columns:
            tree.heading(col, text=col)

        # Đặt độ rộng cột
        tree.column("ID", width=50, anchor="center")
        tree.column("Thời gian", width=150, anchor="center")
        tree.column("Level", width=60, anchor="center")
        tree.column("Tên Level", width=200, anchor="w")
        tree.column("Thuật toán", width=80, anchor="center")
        tree.column("Thời gian chạy", width=120, anchor="center")
        tree.column("Số trạng thái", width=100, anchor="center")
        tree.column("Số bước", width=80, anchor="center")
        tree.column("Chi phí", width=80, anchor="center")

        tree.pack(side="left", fill="both", expand=True)

        # Frame thống kê
        stat_frame = tk.LabelFrame(main_frame, text="📈 Thống kê hiệu suất",
                                   bg="#f0f0f0", font=("Arial", 11, "bold"))
        stat_frame.pack(fill="x", pady=10)

        # Frame nút điều khiển - ĐẢM BẢO NÚT HIỂN THỊ
        btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        btn_frame.pack(fill="x", pady=10)

        def format_time(seconds):
            """Định dạng thời gian với đơn vị phù hợp"""
            if seconds < 0.001:
                return f"{seconds * 1000000:.2f} µs"
            elif seconds < 0.1:
                return f"{seconds * 1000:.3f} ms"
            else:
                return f"{seconds:.6f} s"

        def refresh_history():
            """Làm mới danh sách lịch sử"""
            # Xóa dữ liệu cũ
            for item in tree.get_children():
                tree.delete(item)

            # Lấy dữ liệu với bộ lọc
            level_filter = None if level_var.get() == "Tất cả" else int(level_var.get())
            algo_filter = None if algo_var.get() == "Tất cả" else algo_var.get()

            history = self.history_manager.get_history(level=level_filter, algorithm=algo_filter)

            # Sắp xếp theo thời gian mới nhất
            history = sorted(history, key=lambda x: x["timestamp"], reverse=True)

            # Thêm dữ liệu vào tree
            for record in history:
                formatted_time = format_time(record['execution_time'])
                values = (
                    record["id"],
                    record["timestamp"],
                    record["level"],
                    record["level_name"][:30],
                    record["algorithm"],
                    formatted_time,
                    record["states_explored"],
                    record["solution_length"] if record["solution_length"] else "-",
                    record["cost"] if record["cost"] else "-"
                )
                tree.insert("", "end", values=values)

            # Cập nhật thống kê
            update_statistics()

        def reset_all_data():
            """Xóa toàn bộ dữ liệu lịch sử"""
            if messagebox.askyesno("Xác nhận",
                                   "Bạn có chắc muốn xóa TOÀN BỘ lịch sử?\nHành động này không thể hoàn tác!"):
                self.history_manager.clear_history()
                refresh_history()
                messagebox.showinfo("Thành công", "Đã xóa toàn bộ lịch sử!")

        def update_statistics():
            """Cập nhật thống kê"""
            level_filter = None if level_var.get() == "Tất cả" else int(level_var.get())
            stats = self.history_manager.get_statistics(level=level_filter)

            # Xóa text cũ
            for widget in stat_frame.winfo_children():
                widget.destroy()

            if not stats:
                tk.Label(stat_frame, text="Chưa có dữ liệu thống kê",
                         bg="#f0f0f0", fg="gray").pack(pady=10)
                return

            # Hiển thị thống kê
            row = 0
            for algo, data in stats.items():
                algo_color = {"BFS": "#3498db", "DFS": "#e74c3c", "UCS": "#2ecc71",
                              "Greedy": "#f39c12", "A*": "#9b59b6"}.get(algo, "#333")

                # Khung cho mỗi thuật toán
                algo_frame = tk.Frame(stat_frame, bg="#f0f0f0", relief="solid", bd=1)
                algo_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
                algo_frame.columnconfigure(1, weight=1)

                tk.Label(algo_frame, text=f"📊 {algo}:", font=("Arial", 10, "bold"),
                         bg="#f0f0f0", fg=algo_color).grid(row=0, column=0, sticky="w", padx=5, pady=2)

                # Format thời gian trong thống kê
                avg_time_str = format_time(data['avg_time'])
                min_time_str = format_time(data['min_time'])
                max_time_str = format_time(data['max_time'])

                stats_text = f"Số lần chạy: {data['count']} | "
                stats_text += f"TB: {avg_time_str} | "
                stats_text += f"Nhanh nhất: {min_time_str} | "
                stats_text += f"Chậm nhất: {max_time_str} | "
                stats_text += f"TB số trạng thái: {data['avg_states']:.0f}"

                tk.Label(algo_frame, text=stats_text, font=("Arial", 9),
                         bg="#f0f0f0", fg="#555", wraplength=800, justify="left"
                         ).grid(row=0, column=1, sticky="w", padx=5, pady=2)
                row += 1


        tk.Button(btn_frame, text="🔄 Làm mới", command=refresh_history,
                  bg="#3498db", fg="white", padx=20, pady=8, font=("Arial", 11, "bold"),
                  relief="raised", bd=2).pack(side="left", padx=10)

        # Nút Xóa tất cả dữ liệu - ĐÃ CÓ
        tk.Button(btn_frame, text="🗑️ Xóa tất cả dữ liệu", command=reset_all_data,
                  bg="#e74c3c", fg="white", padx=20, pady=8, font=("Arial", 11, "bold"),
                  relief="raised", bd=2).pack(side="left", padx=10)

        # Nút Đóng
        tk.Button(btn_frame, text="❌ Đóng", command=history_window.destroy,
                  bg="#95a5a6", fg="white", padx=20, pady=8, font=("Arial", 11, "bold"),
                  relief="raised", bd=2).pack(side="right", padx=10)

        # Gắn sự kiện cho combobox
        level_combo.bind("<<ComboboxSelected>>", lambda e: refresh_history())
        algo_combo.bind("<<ComboboxSelected>>", lambda e: refresh_history())

        # Load dữ liệu ban đầu
        refresh_history()


    def clear_history(self, window, refresh_callback):
        """Xóa lịch sử"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa toàn bộ lịch sử?"):
            self.history_manager.clear_history()
            refresh_callback()
            messagebox.showinfo("Thành công", "Đã xóa lịch sử!")


    def show_rule(self):
        level_data = levels[self.level_num]
        rule_text = level_data.get("description", "Không có luật cụ thể cho level này.")

        if self.level_num == 2:
            rule_text += "\n\n Luật cụ thể:\n- Thuyền chở: 1 người + tối đa 2 cừu\n- Cừu hơn kém nhau 1 tuổi (1-2 hoặc 2-3) KHÔNG được ở cùng nhau nếu không có người\n- Cừu 1 và 3 tuổi có thể ở cùng nhau vì chênh lệch 2 tuổi"
        elif self.level_num == 3:
            time_limit = level_data.get("time_limit", 60)
            rule_text += f"\n\n⏱ Thời gian giới hạn: {time_limit} giây\n Bom phải luôn có nhà nghiên cứu giám sát!"
        elif self.level_num == 4:
            weight_limit = level_data.get("weight_limit", 100)
            weights = level_data.get("weights", {})
            rule_text += f"\n\n Thông tin thêm:\n- Giới hạn trọng lượng: {weight_limit}kg\n- Thùng nhỏ: {weights.get('box_small', 30)}kg\n- Thùng trung: {weights.get('box_medium', 60)}kg\n- Thùng lớn: {weights.get('box_large', 90)}kg\n- Thùng nhỏ và thùng vừa không được ở cùng nhau\n- Thùng lớn và thùng nhỏ không được ở cùng nhau"
        elif self.level_num == 5:
            tiger_times = level_data.get("tiger_times", {})
            time_limit = level_data.get("time_limit", 30)
            rule_text += f"\n\n Thông tin thêm:\n- Giới hạn thời gian: {time_limit} giây\n- Hổ nhanh (tiger1): {tiger_times.get('tiger1', 1)} giây\n- Hổ trung bình 1 (tiger2): {tiger_times.get('tiger2', 3)} giây\n- Hổ trung bình 2 (tiger3): {tiger_times.get('tiger3', 6)} giây\n- Hổ chậm (tiger4): {tiger_times.get('tiger4', 8)} giây\n- Hổ rất chậm (tiger5): {tiger_times.get('tiger5', 12)} giây\n\nMỗi lần thuyền qua sông mất thời gian = thời gian của con hổ chậm nhất trên thuyền.\nHổ nhanh (1s,3s) và hổ chậm (8s,12s) không được ở cùng nhau nếu không có hổ 6s."
        elif self.level_num == 6:
            rule_text += """
Lười biếng (scientist1):
   - KHÔNG được ở một mình trên bờ (phải có người khác cùng bờ)
Kiêu ngạo (scientist2):
   - CHỈ thích đi thuyền một mình (không chịu đi cùng ai)
Dũng cảm (person1, person2):
   - Có thể lái thuyền và đi với bất kỳ ai
"""
        elif self.level_num == 7:
            move_limit = level_data.get("move_limit", 5)
            rule_text += f"\n\n Bom sẽ nổ sau {move_limit} lượt di chuyển!\n🐺 Sói không được ăn Cừu khi không có Người"
        elif self.level_num == 8:
            rule_text += "\n\n Luật:\n- Sói ăn Cừu nếu không có Người\n- Bom không được ở với Cừu nếu không có Người\n- Robot phải đi cùng Người"
        elif self.level_num == 9:
            rule_text += "\n\n Luật:\n- Robot không được đi một mình\n- Bom có thể đi tự do"
        elif self.level_num == 10:
            rule_text += "\n\n Luật:\n- Nếu số Hổ nhiều hơn số Sói ở bất kỳ bờ nào, Sói sẽ bị ăn"

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
            level_data=level_data,
            boat_side=0
        )

        self.selected = []
        self.steps = 0
        self.start_time = time.time()
        self.time_elapsed = 0
        self.game_over = False

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

        # Khung điều khiển bên phải (chỉ có control, không có lịch sử cố định)
        control = tk.Frame(main, width=260, bg="#eeeeee")
        control.pack(side="right", fill="y")
        control.pack_propagate(False)

        self.canvas = tk.Canvas(game_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

        tk.Label(control, text=f" LEVEL {level}: {level_data['name']}",
                 font=("Arial", 10, "bold"), bg="#eeeeee").pack(pady=5)

        max_items = level_data["boat_capacity"] - 1
        if level == 4:
            max_items = 1  # Level 4 chỉ chở được 1 vật
        tk.Label(control, text=f" Sức chứa: {level_data['boat_capacity']} (tối đa {max_items} vật)",
                 font=("Arial", 9), bg="#eeeeee", fg="blue").pack(pady=5)

        if level == 2:
            tk.Label(control, text=f"🐑 Luật: Cừu chênh lệch 1 tuổi không ở cùng nhau nếu không có người",
                     font=("Arial", 8), bg="#eeeeee", fg="red", wraplength=240).pack(pady=2)
        elif level == 3:
            time_limit = level_data.get("time_limit", 60)
            tk.Label(control, text=f" Thời gian giới hạn: {time_limit} giây",
                     font=("Arial", 9), bg="#eeeeee", fg="green").pack(pady=2)
            tk.Label(control, text=f" Bom phải có nhà nghiên cứu giám sát",
                     font=("Arial", 8), bg="#eeeeee", fg="red", wraplength=240).pack(pady=2)
        elif level == 4:
            weight_limit = level_data.get("weight_limit", 100)
            tk.Label(control, text=f" Giới hạn trọng lượng: {weight_limit}kg",
                     font=("Arial", 9), bg="#eeeeee", fg="green").pack(pady=2)
        elif level == 5:
            time_limit = level_data.get("time_limit", 30)
            tk.Label(control, text=f" Tối ưu thời gian (≤{time_limit}s)",
                     font=("Arial", 9), bg="#eeeeee", fg="green").pack(pady=2)
        elif level == 6:
            tk.Label(control, text=f" Lười: KHÔNG ở một mình",
                     font=("Arial", 7), bg="#eeeeee", fg="red", wraplength=240).pack(pady=2)
            tk.Label(control, text=f" Kiêu: CHỈ đi thuyền một mình",
                     font=("Arial", 7), bg="#eeeeee", fg="red", wraplength=240).pack(pady=2)
            tk.Label(control, text=f" Dũng cảm: Có thể lái thuyền",
                     font=("Arial", 7), bg="#eeeeee", fg="green", wraplength=240).pack(pady=2)
        elif level == 7:
            move_limit = level_data.get("move_limit", 5)
            tk.Label(control, text=f" Bom sẽ nổ sau {move_limit} lượt",
                     font=("Arial", 9), bg="#eeeeee", fg="red").pack(pady=2)

        self.info_label = tk.Label(control, text="", bg="#eeeeee", justify="left")
        self.info_label.pack(pady=10)
        self.status_label = tk.Label(control, text="", bg="#eeeeee", justify="left")
        self.status_label.pack(pady=10)

        # Frame cho các nút (sắp xếp thành 3 hàng cho gọn)
        buttons_frame1 = tk.Frame(control, bg="#eeeeee")
        buttons_frame1.pack(pady=5)

        buttons_frame2 = tk.Frame(control, bg="#eeeeee")
        buttons_frame2.pack(pady=5)

        buttons_frame3 = tk.Frame(control, bg="#eeeeee")
        buttons_frame3.pack(pady=5)

        buttons_frame4 = tk.Frame(control, bg="#eeeeee")
        buttons_frame4.pack(pady=5)

        # Hàng 1: Rule, Chở, Hint
        self.make_button(buttons_frame1, "Rule", "black", "#d3d3d3", "#c0c0c0", self.show_rule).pack(side="left",
                                                                                                     padx=3)
        self.make_button(buttons_frame1, "Chở", "black", "#f0e68c", "#e6d96c", self.move_boat).pack(side="left", padx=3)
        self.make_button(buttons_frame1, "Hint", "darkorange", "#ffe4b5", "#ffdead", self.use_hint).pack(side="left",
                                                                                                         padx=3)

        # Hàng 2: BFS, DFS, A*
        self.make_button(buttons_frame2, "BFS", "darkblue", "#add8e6", "#87ceeb", self.solve_bfs).pack(side="left",
                                                                                                       padx=3)
        self.make_button(buttons_frame2, "DFS", "darkred", "#f08080", "#cd5c5c", self.solve_dfs).pack(side="left",
                                                                                                      padx=3)
        self.make_button(buttons_frame2, "A*", "darkgreen", "#90ee90", "#66cdaa", self.solve_astar).pack(side="left",
                                                                                                         padx=3)

        # Hàng 3: UCS, Greedy, Reset
        self.make_button(buttons_frame3, "UCS", "darkcyan", "#e0ffff", "#afeeee", self.solve_ucs).pack(side="left",
                                                                                                       padx=3)
        self.make_button(buttons_frame3, "Greedy", "darkorange", "#ffebcd", "#ffdead", self.solve_greedy).pack(
            side="left", padx=3)
        self.make_button(buttons_frame3, "Reset", "purple", "#dda0dd", "#ba55d3", self.start_game).pack(side="left",
                                                                                                        padx=3)

        # Hàng 4: Menu và Xem lịch sử
        self.make_button(buttons_frame4, "Menu", "brown", "#f5deb3", "#e6c68a", self.show_start).pack(side="left",
                                                                                                      padx=3)
        self.make_button(buttons_frame4, "📜 Lịch sử", "white", "#4CAF50", "#45a049", self.show_history_in_game).pack(
            side="left", padx=3)

        self.load_images()
        self.draw()
        self.update_timer()

    def show_history_in_game(self):
        """Hiển thị lịch sử dưới dạng cửa sổ popup nhỏ gọn trong game"""

        # Kiểm tra nếu chưa có level_num (đang ở menu)
        if not hasattr(self, 'level_num'):
            # Nếu chưa có level, hiển thị thông báo và gọi show_history tổng quát
            messagebox.showinfo("Thông báo", "Vui lòng chọn level trước khi xem lịch sử!")
            self.show_history()  # Gọi lịch sử tổng quát
            return

        # Tạo cửa sổ popup
        history_window = tk.Toplevel(self.root)
        history_window.title(f"Lịch sử AI - Level {self.level_num}")
        history_window.geometry("500x450")
        history_window.configure(bg="#f0f0f0")
        history_window.transient(self.root)  # Đặt làm con của cửa sổ chính
        history_window.grab_set()  # Modal

        # Center window
        history_window.update_idletasks()
        x = (history_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (history_window.winfo_screenheight() // 2) - (450 // 2)
        history_window.geometry(f"500x450+{x}+{y}")

        # Frame chính
        main_frame = tk.Frame(history_window, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tiêu đề
        level_data = levels[self.level_num]
        title_text = f"📊 LỊCH SỬ AI - {level_data['name']}"
        tk.Label(main_frame, text=title_text, font=("Arial", 14, "bold"),
                 bg="#f0f0f0", fg="#333").pack(pady=10)

        # Frame hiển thị lịch sử
        history_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
        history_frame.pack(fill="both", expand=True, pady=10)

        # Text widget hiển thị lịch sử
        history_text = tk.Text(history_frame, height=18, width=55,
                               bg="white", fg="#333", font=("Courier", 9),
                               wrap="word", state="disabled")
        history_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = tk.Scrollbar(history_frame, command=history_text.yview)
        scrollbar.pack(side="right", fill="y")
        history_text.config(yscrollcommand=scrollbar.set)

        # Cấu hình tag màu sắc
        history_text.tag_config("header", font=("Courier", 10, "bold"), foreground="#2c3e50")
        history_text.tag_config("separator", foreground="#7f8c8d")
        history_text.tag_config("bfs", foreground="#2980b9")
        history_text.tag_config("dfs", foreground="#c0392b")
        history_text.tag_config("ucs", foreground="#27ae60")
        history_text.tag_config("greedy", foreground="#f39c12")
        history_text.tag_config("astar", foreground="#8e44ad")
        history_text.tag_config("stats", foreground="#16a085")
        history_text.tag_config("info", foreground="#95a5a6")

        # Lấy dữ liệu lịch sử cho level hiện tại
        history = self.history_manager.get_history(level=self.level_num)

        # Cập nhật nội dung
        history_text.config(state="normal")
        history_text.delete(1.0, tk.END)

        if not history:
            history_text.insert(tk.END, "🤖 Chưa có lịch sử chạy AI cho level này\n\n", "header")
            history_text.insert(tk.END, "Hãy thử chạy một thuật toán:\n", "info")
            history_text.insert(tk.END, "• BFS - Tìm đường ngắn nhất\n", "info")
            history_text.insert(tk.END, "• DFS - Tìm kiếm chiều sâu\n", "info")
            history_text.insert(tk.END, "• UCS - Tối ưu chi phí\n", "info")
            history_text.insert(tk.END, "• Greedy - Heuristic thuần\n", "info")
            history_text.insert(tk.END, "• A* - Kết hợp g + h\n", "info")
        else:
            # Header
            history_text.insert(tk.END, "═" * 50 + "\n", "separator")
            history_text.insert(tk.END, f"{'THỜI GIAN':<20} {'THUẬT TOÁN':<12} {'SỐ NODE':<10} {'THỜI GIAN':<10}\n",
                                "header")
            history_text.insert(tk.END, "─" * 50 + "\n", "separator")

            # Hiển thị các bản ghi (mới nhất ở trên)
            for record in reversed(history[-15:]):  # Hiển thị 15 bản ghi gần nhất
                timestamp = record["timestamp"][5:16]  # Lấy MM-DD HH:MM
                algo = record["algorithm"]
                nodes = record["states_explored"]
                time_str = f"{record['execution_time']:.3f}s"

                # Chọn màu theo thuật toán
                tag = algo.lower()
                if tag == "bfs":
                    tag = "bfs"
                elif tag == "dfs":
                    tag = "dfs"
                elif tag == "ucs":
                    tag = "ucs"
                elif tag == "greedy":
                    tag = "greedy"
                elif tag == "a*":
                    tag = "astar"

                line = f"{timestamp:<20} {algo:<12} {nodes:<10} {time_str:<10}\n"
                history_text.insert(tk.END, line, tag)

            history_text.insert(tk.END, "═" * 50 + "\n", "separator")

            # Thống kê
            stats = self.history_manager.get_statistics(level=self.level_num)
            if stats:
                history_text.insert(tk.END, "\n📈 THỐNG KÊ HIỆU SUẤT:\n", "stats")
                for algo, data in stats.items():
                    tag = algo.lower()
                    line = f"  {algo:<8}: {data['count']} lần | "
                    line += f"TB {data['avg_time']:.3f}s | "
                    line += f"Min {data['min_time']:.3f}s | "
                    line += f"Max {data['max_time']:.3f}s\n"
                    history_text.insert(tk.END, line, tag if tag in ["bfs", "dfs", "ucs", "greedy", "astar"] else None)

        history_text.config(state="disabled")

        # Frame nút điều khiển
        btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        btn_frame.pack(fill="x", pady=10)

        def refresh_history():
            """Làm mới hiển thị lịch sử"""
            history_text.config(state="normal")
            history_text.delete(1.0, tk.END)

            new_history = self.history_manager.get_history(level=self.level_num)

            if not new_history:
                history_text.insert(tk.END, "🤖 Chưa có lịch sử chạy AI cho level này\n\n", "header")
                history_text.insert(tk.END, "Hãy thử chạy một thuật toán!\n", "info")
            else:
                history_text.insert(tk.END, "═" * 50 + "\n", "separator")
                history_text.insert(tk.END, f"{'THỜI GIAN':<20} {'THUẬT TOÁN':<12} {'SỐ NODE':<10} {'THỜI GIAN':<10}\n",
                                    "header")
                history_text.insert(tk.END, "─" * 50 + "\n", "separator")

                def format_time(seconds):
                    """Định dạng thời gian với đơn vị phù hợp"""
                    if seconds < 0.001:
                        return f"{seconds * 1000000:.2f}µs"
                    elif seconds < 0.1:
                        return f"{seconds * 1000:.3f}ms"
                    else:
                        return f"{seconds:.3f}s"

                for record in reversed(history[-15:]):
                    timestamp = record["timestamp"][5:16]
                    algo = record["algorithm"]
                    nodes = record["states_explored"]
                    time_str = format_time(record['execution_time'])

                    tag = algo.lower()
                    if tag == "bfs":
                        tag = "bfs"
                    elif tag == "dfs":
                        tag = "dfs"
                    elif tag == "ucs":
                        tag = "ucs"
                    elif tag == "greedy":
                        tag = "greedy"
                    elif tag == "a*":
                        tag = "astar"

                    line = f"{timestamp:<20} {algo:<12} {nodes:<10} {time_str:<10}\n"
                    history_text.insert(tk.END, line, tag)

                history_text.insert(tk.END, "═" * 50 + "\n", "separator")

                stats = self.history_manager.get_statistics(level=self.level_num)
                if stats:
                    history_text.insert(tk.END, "\n📈 THỐNG KÊ HIỆU SUẤT:\n", "stats")
                    for algo, data in stats.items():
                        tag = algo.lower()
                        line = f"  {algo:<8}: {data['count']} lần | "
                        line += f"TB {data['avg_time']:.3f}s | "
                        line += f"Min {data['min_time']:.3f}s | "
                        line += f"Max {data['max_time']:.3f}s\n"
                        history_text.insert(tk.END, line,
                                            tag if tag in ["bfs", "dfs", "ucs", "greedy", "astar"] else None)

            history_text.config(state="disabled")

        # Nút làm mới
        tk.Button(btn_frame, text="🔄 Làm mới", command=refresh_history,
                  bg="#3498db", fg="white", padx=15, pady=5).pack(side="left", padx=5)

        # Nút xóa lịch sử level này
        def clear_level_history():
            if messagebox.askyesno("Xác nhận", f"Xóa lịch sử cho Level {self.level_num}?"):
                # Lưu lại lịch sử của các level khác
                other_history = [r for r in self.history_manager.history if r["level"] != self.level_num]
                self.history_manager.history = other_history
                self.history_manager.save_history()
                refresh_history()
                messagebox.showinfo("Thành công", f"Đã xóa lịch sử Level {self.level_num}!")

        tk.Button(btn_frame, text="🗑️ Xóa level này", command=clear_level_history,
                  bg="#e74c3c", fg="white", padx=15, pady=5).pack(side="left", padx=5)

        # Nút đóng
        tk.Button(btn_frame, text="❌ Đóng", command=history_window.destroy,
                  bg="#95a5a6", fg="white", padx=15, pady=5).pack(side="right", padx=5)

    def get_display_name(self, char_name):
        level_data = levels[self.level_num]

        if self.level_num == 2:
            if char_name == "sheep1":
                return " Cừu 1 tuổi"
            elif char_name == "sheep2":
                return " Cừu 2 tuổi"
            elif char_name == "sheep3":
                return " Cừu 3 tuổi"
        elif self.level_num == 4:
            weights = level_data.get("weights", {})
            if char_name == "box_small":
                return f" Thùng nhỏ ({weights.get('box_small', 30)}kg)"
            elif char_name == "box_medium":
                return f" Thùng trung ({weights.get('box_medium', 60)}kg)"
            elif char_name == "box_large":
                return f" Thùng lớn ({weights.get('box_large', 90)}kg)"
        elif self.level_num == 5:
            tiger_times = level_data.get("tiger_times", {})
            if char_name in tiger_times:
                time_val = tiger_times[char_name]
                if char_name == "tiger1":
                    return f" Hổ nhanh ({time_val}s)"
                elif char_name == "tiger2":
                    return f" Hổ TB 1 ({time_val}s)"
                elif char_name == "tiger3":
                    return f" Hổ TB 2 ({time_val}s)"
                elif char_name == "tiger4":
                    return f" Hổ chậm ({time_val}s)"
                elif char_name == "tiger5":
                    return f" Hổ rất chậm ({time_val}s)"
        elif self.level_num == 6:
            if char_name == "person1":
                return "Dũng cảm 1"
            elif char_name == "person2":
                return "Dũng cảm 2"
            elif char_name == "scientist1":
                return "Lười biếng"
            elif char_name == "scientist2":
                return "Kiêu ngạo"
        return char_name

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

    def draw(self):
        self.canvas.delete("all")

        self.canvas.create_image(0, 0, anchor="nw", image=self.images["bg"])
        self.canvas.create_image(self.boat_x, 420, image=self.images["boat"])

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        characters = levels[self.level_num]["characters"]

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

            if name in self.images:
                self.canvas.create_image(x, y, image=self.images[name], tags=name, anchor="center")

            if self.level_num in [2, 4, 5, 6]:
                display_name = self.get_display_name(name)
                text_y_offset = 55
                if self.level_num == 5 and len(display_name) > 15:
                    text_y_offset = 65
                if self.level_num == 6:
                    text_y_offset = 65
                self.canvas.create_text(
                    x, y + text_y_offset,
                    text=display_name,
                    font=("Arial", 8, "bold"),
                    fill="white",
                    tags=f"{name}_label"
                )

            if name in self.selected:
                self.canvas.create_rectangle(x - 45, y - 45, x + 45, y + 55, outline="red", width=3)
            elif side != self.state.boat_side:
                self.canvas.create_rectangle(x - 45, y - 45, x + 45, y + 55, outline="gray", width=2)

        info_text = "TRẠNG THÁI:\n"
        for i, name in enumerate(characters):
            side_text = " Phải" if self.state.state[i] else " Trái"
            display_name = self.get_display_name(name)
            info_text += f"{display_name}: {side_text}\n"

        max_items = self.state.boat_capacity - 1
        if self.level_num == 4:
            max_items = 1

        if self.level_num == 6:
            if len(self.selected) > 0:
                driver = self.selected[0]
                selected_items = [item for item in self.selected if item != driver]
            else:
                selected_items = []
        else:
            selected_items = [item for item in self.selected if item != "person" and item != "scientist"]

        info_text += f"Đã chọn: {len(selected_items)}/{max_items} vật"

        self.info_label.config(text=info_text)

    def on_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        tags = self.canvas.gettags(item)
        if not tags:
            return
        name = tags[0]

        if name.endswith("_label"):
            return

        characters = levels[self.level_num]["characters"]
        if name not in characters:
            return

        idx = characters.index(name)

        if self.state.state[idx] != self.state.boat_side:
            messagebox.showwarning("Không thể chọn", f"{self.get_display_name(name)} không ở cùng bờ với thuyền!")
            return

        max_items = self.state.boat_capacity - 1
        if self.level_num == 4:
            max_items = 1

        if self.level_num == 6:
            if len(self.selected) > 0:
                driver = self.selected[0]
                selected_items = [item for item in self.selected if item != driver]
            else:
                selected_items = []
        else:
            selected_items = [item for item in self.selected if item != "person" and item != "scientist"]

        if name in self.selected:
            self.selected.remove(name)
        else:
            if self.level_num == 6:
                if len(self.selected) == 0:
                    self.selected.append(name)
                else:
                    if len(selected_items) >= max_items:
                        messagebox.showwarning("Quá tải", f"Thuyền chỉ chở được tối đa {max_items} vật cùng lúc!")
                        return
                    self.selected.append(name)
            else:
                if name != "person" and name != "scientist":
                    if len(selected_items) >= max_items:
                        messagebox.showwarning("Quá tải", f"Thuyền chỉ chở được tối đa {max_items} vật cùng lúc!")
                        return
                self.selected.append(name)

        self.draw()

    def move_boat(self, callback=None):
        characters = levels[self.level_num]["characters"]

        has_driver = False
        driver_name = None


        if self.level_num == 6:
            if len(self.selected) > 0:
                has_driver = True
                driver_name = self.selected[0]
        else:
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

        # Level 4 chỉ cho chở tối đa 1 vật
        if self.level_num == 4:
            max_items = 1

        # Kiểm tra số lượng vật
        if len(selected_items) > max_items:
            messagebox.showwarning("Lỗi", f"Thuyền chỉ chở được tối đa {max_items} vật cùng lúc!")
            return

        # Kiểm tra trọng lượng cho Level 4
        if self.level_num == 4:
            weights = levels[4].get("weights", {})
            weight_limit = levels[4].get("weight_limit", 100)
            total_weight = 0
            for item in selected_items:
                total_weight += weights.get(item, 0)
            if total_weight > weight_limit:
                messagebox.showwarning("Lỗi", f"Tổng trọng lượng {total_weight}kg vượt quá giới hạn {weight_limit}kg!")
                return

        if len(selected_items) > max_items:
            messagebox.showwarning("Lỗi", f"Thuyền chỉ chở được tối đa {max_items} vật cùng lúc!")
            return

        self.current_driver = driver_name

        target = self.right_boat if self.state.boat_side == 0 else self.left_boat
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
        self.boat_x = self.right_boat if self.state.boat_side else self.left_boat
        self.selected.clear()
        self.draw()
        self.steps += 1

        if self.level_num == 7:
            bomb_idx = self.state.characters.index("bomb")
            if self.state.state[bomb_idx] == 0:
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
            self.boat_x = self.right_boat if self.state.boat_side else self.left_boat
            self.draw()
        else:
            messagebox.showinfo("Hint", "Không tìm thấy gợi ý!")

    def show_ai_result(self, algo_name, exec_time, explored):
        if exec_time < 0.001:
            time_str = f"{exec_time * 1000000:.2f} µs"
        elif exec_time < 0.1:
            time_str = f"{exec_time * 1000:.3f} ms"
        else:
            time_str = f"{exec_time:.6f} s"

        res_msg = (f"--- THỐNG KÊ GIẢI THUẬT ---\n"
                   f"🤖 Thuật toán: {algo_name}\n"
                   f"⏱️ Thời gian giải: {time_str}\n"
                   f"🧩 Số trạng thái đã duyệt: {explored}\n"
                   f"---------------------------")
        messagebox.showinfo("Kết quả AI", res_msg)

    def run_solve(self, algo_func, name):
        try:
            # Gọi thuật toán (trả về 5 giá trị)
            result = algo_func(self.state)

            if len(result) == 5:
                sol, t, nodes, sol_length, cost = result
            else:
                # Fallback cho các hàm cũ
                sol, t, nodes = result
                sol_length = len(sol) - 1 if sol else None
                cost = sol[-1].cost if sol else None

            if sol:
                # Lưu vào lịch sử
                self.history_manager.add_record(
                    level=self.level_num,
                    algorithm=name,
                    exec_time=t,
                    states_explored=nodes,
                    solution_length=sol_length,
                    cost=cost
                )


                self.show_ai_result(name, t, nodes)
                self.animate_solution(sol)
            else:
                messagebox.showwarning("Thông báo", f"{name} không tìm thấy lời giải!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thực thi {name}: {e}")

    def solve_bfs(self):
        self.run_solve(bfs, "BFS")

    def solve_dfs(self):
        self.run_solve(dfs, "DFS")

    def solve_ucs(self):
        self.run_solve(ucs, "UCS")

    def solve_greedy(self):
        self.run_solve(greedy, "Greedy")

    def solve_astar(self):
        self.run_solve(astar, "A*")

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
        if hasattr(self, 'game_over') and self.game_over:
            return

        if self.level_num == 3:
            time_limit = levels[self.level_num].get("time_limit", 60)
            time_left = max(0, time_limit - self.time_elapsed)
            status_text = f"⏱️ Thời gian: {self.time_elapsed} giây\n⏰ Còn lại: {time_left} giây\n📊 Số bước: {self.steps}"

            if self.time_elapsed >= time_limit and not self.state.is_goal() and not self.game_over:
                self.game_over = True
                messagebox.showinfo("Thất bại", f"Hết giờ! Bạn đã thua Level {self.level_num}!")
                self.show_level_menu()
                return

        elif self.level_num == 5:
            cost = getattr(self.state, 'cost', 0)
            status_text = f"⏱️ Thời gian thực: {self.time_elapsed} giây\n Tổng thời gian di chuyển: {cost} giây\n Số bước: {self.steps}"

            time_limit = levels[self.level_num].get("time_limit", 30)
            if self.state.cost > time_limit and not self.state.is_goal() and not self.game_over:
                self.game_over = True
                messagebox.showinfo("Thất bại",
                                    f"Tổng thời gian di chuyển {self.state.cost} giây vượt quá giới hạn {time_limit} giây!")
                self.show_level_menu()
                return

        elif self.level_num == 7:
            bomb_idx = self.state.characters.index("bomb")
            bomb_side = self.state.state[bomb_idx]

            if bomb_side == 0:
                remaining = max(0, self.move_limit - self.state.moves)
                status_text = f"💣 Bom ở bờ trái\n Số lượt còn lại: {remaining}/{self.move_limit}\n Số bước: {self.steps}"

                if self.state.moves >= self.move_limit and not self.state.is_goal() and not self.game_over:
                    self.game_over = True
                    messagebox.showinfo("Thất bại", f"Bom đã nổ! Bạn đã thua Level {self.level_num}!")
                    self.show_level_menu()
                    return
            else:
                status_text = f"💣 Bom đã qua sông an toàn\n Số bước: {self.steps}"

        else:
            status_text = f" Thời gian: {self.time_elapsed} giây\n Số bước: {self.steps}"

        self.status_label.config(text=status_text)

    def clear(self):
        for w in self.frame.winfo_children():
            w.destroy()