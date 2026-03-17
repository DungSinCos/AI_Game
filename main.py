import tkinter as tk
from ui import GameUI

root = tk.Tk()
root.title("River Crossing Game")

root.state("zoomed")   # Windows


GameUI(root)

root.mainloop()