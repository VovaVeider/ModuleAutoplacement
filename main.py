"""
main.py
Точка входа в приложение.
"""

import tkinter as tk
from tabmanager import TabManager
from globalmenu import GlobalMenu

def main():
    root = tk.Tk()
    root.title("Редактор схем РГРТУ")
    root.geometry("1024x768")
    tab_manager = TabManager(root)
    global_menu = GlobalMenu(root, tab_manager)
    root.mainloop()

if __name__ == "__main__":
    main()
