import tkinter as tk

# Importamos nuestra propia interfaz desde la carpeta ui
from ui.interfaz import InterfazApp

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1280x800")

    app = InterfazApp(root)

    root.mainloop()