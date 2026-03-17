import tkinter as tk
from PIL import Image, ImageTk
from game_logic import GameState
from ai import bfs, hint

class GameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("River Crossing Game")

        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        self.show_start()

    # ================= START SCREEN =================
    def show_start(self):
        self.clear()

        tk.Label(self.frame, text="🌊 River Crossing Game", font=("Arial", 24)).pack(pady=50)

        tk.Button(self.frame, text="▶ Play", width=20, command=self.show_menu).pack(pady=10)

    # ================= MENU =================
    def show_menu(self):
        self.clear()

        tk.Label(self.frame, text="Chọn Level", font=("Arial", 16)).pack()

        self.level = tk.IntVar(value=1)
        for i in range(1, 6):  # demo 5 level, bạn có thể lên 15
            tk.Radiobutton(self.frame, text=f"Level {i}", variable=self.level, value=i).pack()

        tk.Label(self.frame, text="Chọn thuật toán", font=("Arial", 16)).pack(pady=10)

        self.algo = tk.StringVar(value="BFS")
        tk.Radiobutton(self.frame, text="BFS", variable=self.algo, value="BFS").pack()
        tk.Radiobutton(self.frame, text="DFS", variable=self.algo, value="DFS").pack()
        tk.Radiobutton(self.frame, text="A*", variable=self.algo, value="A*").pack()

        tk.Button(self.frame, text="▶ Start Game", command=self.start_game).pack(pady=20)

    # ================= GAME =================
    def start_game(self):
        self.clear()

        self.state = GameState()
        self.selected = []
        self.boat_side = 0

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # 🚀 chia layout: game + control
        game_frame = tk.Frame(self.frame)
        game_frame.pack(fill="both", expand=True)

        control_frame = tk.Frame(self.frame, height=80, bg="lightgray")
        control_frame.pack(fill="x")

        # 🎮 canvas (KHÔNG full toàn màn nữa)
        self.canvas = tk.Canvas(
            game_frame,
            width=screen_w,
            height=screen_h - 80  # chừa chỗ cho nút
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.on_click)

        # 🚤 vị trí thuyền
        self.boat_x = int(screen_w * 0.35)

        # 🎛️ nút điều khiển
        tk.Button(control_frame, text="🚤 Chở", command=self.move_boat) \
            .pack(side="left", padx=10, pady=10)

        tk.Button(control_frame, text="💡 Hint", command=self.use_hint) \
            .pack(side="left", padx=10)

        tk.Button(control_frame, text="🤖 AI Solve", command=self.solve) \
            .pack(side="left", padx=10)

        tk.Button(control_frame, text="🔄 Reset", command=self.start_game) \
            .pack(side="left", padx=10)

        tk.Button(control_frame, text="🏠 Menu", command=self.show_start) \
            .pack(side="right", padx=10)

        self.load_images()
        self.draw()

    # ================= LOAD IMAGE =================
    def load_images(self):
        # lấy kích thước màn hình
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        def load(path, size=None):
            img = Image.open("assets/" + path)
            if size:
                img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)

        self.images = {
            # background full màn hình
            "bg": load("bg.png", (screen_w, screen_h)),

            # object nhỏ lại cho đẹp
            "person": load("person.png", (130, 130)),
            "wolf": load("wolf.png", (130, 130)),
            "sheep": load("sheep.png", (130, 130)),
            "cabbage": load("cabbage.png", (130, 130)),

            # thuyền to hơn
            "boat": load("boat.png", (250, 200))
        }


    # ================= DRAW =================
    def draw(self):
        self.canvas.delete("all")

        screen_w = self.root.winfo_screenwidth()
        LEFT_X = int(screen_w * 0.2)
        RIGHT_X = int(screen_w * 0.8)
        BOAT_Y = int(self.root.winfo_screenheight() * 0.65)

        screen_h = self.root.winfo_screenheight()

        self.canvas.create_image(screen_w // 2, screen_h // 2, image=self.images["bg"])

        BOAT_Y = 400
        self.canvas.create_image(self.boat_x, BOAT_Y, image=self.images["boat"])

        LEFT_X = 150
        RIGHT_X = 750

        positions = {
            "person": 100,
            "wolf": 200,
            "sheep": 300,
            "cabbage": 400
        }

        for name,y in positions.items():
            idx = {"person":0,"wolf":1,"sheep":2,"cabbage":3}[name]
            side = self.state.state[idx]

            if name in self.selected:
                index = self.selected.index(name)
                spacing = 70
                start_x = self.boat_x - spacing // 2
                x = start_x + index * spacing
            else:
                x = LEFT_X if side == 0 else RIGHT_X

            self.canvas.create_image(x,y,image=self.images[name],tags=name)

            if name in self.selected:
                self.canvas.create_rectangle(x-30,y-30,x+30,y+30,outline="red",width=2)


    def on_click(self,event):
        item = self.canvas.find_closest(event.x,event.y)
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

    def move_boat(self):
        screen_w = self.root.winfo_screenwidth()
        left_boat = int(screen_w * 0.35)
        right_boat = int(screen_w * 0.65)

        target = right_boat if self.boat_side == 0 else left_boat

        if "person" not in self.selected:
            return

        target = 600 if self.boat_side == 0 else 300
        step = 5 if target > self.boat_x else -5

        def animate():
            if (step>0 and self.boat_x<target) or (step<0 and self.boat_x>target):
                self.boat_x += step
                self.draw()
                self.root.after(20,animate)
            else:
                self.finish_move()

        animate()

    def finish_move(self):
        new_state = self.state.move(self.selected)
        if not new_state:
            self.selected.clear()
            self.draw()
            return

        self.state = new_state
        self.boat_side = 1 - self.boat_side
        self.selected.clear()

        self.draw()

    # ================= AI =================
    def use_hint(self):
        h = hint(self.state)
        if h:
            self.state = h
            self.draw()

    def solve(self):
        sol = bfs(self.state)
        if sol:
            self.animate_solution(sol)

    def animate_solution(self, sol, i=0):
        if i >= len(sol):
            return
        self.state = sol[i]
        self.draw()
        self.root.after(700, lambda: self.animate_solution(sol,i+1))

    # ================= UTILITY =================
    def clear(self):
        for widget in self.frame.winfo_children():
            widget.destroy()