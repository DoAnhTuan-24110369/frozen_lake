import tkinter as tk
from ui import FrozenLakeGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = FrozenLakeGUI(root)
    root.mainloop()