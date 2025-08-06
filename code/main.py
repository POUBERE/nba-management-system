import tkinter as tk
from tkinter import messagebox
# from nba_api_client import NBAGuiWithAPI
from nba_gui import NBAGui


def main():
    """Fonction principale pour lancer l'application"""
    root = tk.Tk()

    # Configuration de l'icône (optionnel)
    try:
        root.iconphoto(False, tk.PhotoImage(data=""))  # Placeholder pour icône
    except:
        pass

    app = NBAGui(root)
    # Utiliser la version étendue avec API
    # app = NBAGuiWithAPI(root)  # Au lieu de NBAGui(root)

    # Centrer la fenêtre sur l'écran
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # Configuration pour la fermeture
    def on_closing():
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter le système NBA?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Lancer l'application
    root.mainloop()


if __name__ == "__main__":
    main()
