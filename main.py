import tkinter as tk
from ui import GameUI

root = tk.Tk()
root.title("River Crossing Game")

#root.state("zoomed")   # Windows
root.geometry("1200x750")

GameUI(root)

root.mainloop()