import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from nba_system import NBASystem
from joueur import PosteJoueur
from nba_system import ValidationError
import json


class NBAGui:
    def __init__(self, root):
        self.root = root
        self.root.title("🏀 Système de Gestion NBA")

        # Fenêtre plus petite au démarrage, centrée
        self.center_window(1000, 700)

        # Configuration de redimensionnement avec taille minimale réduite
        self.root.minsize(800, 600)

        # Configuration responsive - TRÈS IMPORTANT
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.root.configure(bg='#2c3e50')

        # Initialiser le système NBA
        self.nba_system = NBASystem()

        # Configuration du style
        self.setup_styles()

        # Variables pour le thème
        self.colors = {
            'primary': '#3498db',
            'secondary': '#e74c3c',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'darker': '#1a252f'
        }

        self.setup_ui()
        self.charger_donnees_exemple()

        # Bind pour redimensionnement avec debounce
        self.resize_after_id = None
        self.root.bind('<Configure>', self.on_window_resize)

    def center_window(self, width, height):
        """Centrer la fenêtre sur l'écran"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def on_window_resize(self, event):
        """Gérer le redimensionnement de la fenêtre avec debounce"""
        if event.widget == self.root:
            # Annuler le précédent appel si il existe
            if self.resize_after_id:
                self.root.after_cancel(self.resize_after_id)

            # Programmer l'ajustement après un délai
            self.resize_after_id = self.root.after(100, self.adjust_ui_scaling)

    def adjust_ui_scaling(self):
        """Ajuster l'échelle de l'UI selon la taille de la fenêtre"""
        try:
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()

            # Ajuster les tailles de police selon la largeur
            if current_width < 900:
                header_font_size = 18
                subtitle_font_size = 10
                label_font_size = 9
                button_padding = [8, 4]
            elif current_width < 1200:
                header_font_size = 22
                subtitle_font_size = 11
                label_font_size = 10
                button_padding = [10, 5]
            else:
                header_font_size = 24
                subtitle_font_size = 12
                label_font_size = 10
                button_padding = [12, 6]

            # Mettre à jour les styles des boutons
            self.style.configure('Action.TButton', padding=button_padding)
            self.style.configure('Success.TButton', padding=button_padding)
            self.style.configure('Danger.TButton', padding=button_padding)

            # Ajuster la hauteur des éléments selon la hauteur de la fenêtre
            if current_height < 650:
                tree_height = 4
                text_height = 6
            elif current_height < 800:
                tree_height = 5
                text_height = 8
            else:
                tree_height = 6
                text_height = 10

            # Mettre à jour les treeviews existants
            for tree_name in ['equipes_tree', 'joueurs_tree', 'matchs_tree', 'classement_tree', 'top_tree']:
                if hasattr(self, tree_name):
                    getattr(self, tree_name).configure(height=tree_height)

            # Mettre à jour les zones de texte
            if hasattr(self, 'stats_general_text'):
                self.stats_general_text.configure(height=text_height)
            if hasattr(self, 'comparaison_text'):
                self.comparaison_text.configure(height=max(6, text_height-2))
            if hasattr(self, 'analyse_text'):
                self.analyse_text.configure(height=max(8, text_height+2))

        except tk.TclError:
            # Ignorer les erreurs si les widgets n'existent pas encore
            pass

    def bind_mousewheel(self, widget, canvas):
        """Lier la molette de la souris et le pavé tactile au canvas"""
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_shift_mousewheel(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        # Fonction pour bind récursif sur tous les widgets enfants
        def bind_to_all_children(widget):
            # Bind sur le widget lui-même
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Shift-MouseWheel>", _on_shift_mousewheel)
            widget.bind(
                "<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            widget.bind(
                "<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
            widget.bind("<Shift-Button-4>",
                        lambda e: canvas.xview_scroll(-1, "units"))
            widget.bind("<Shift-Button-5>",
                        lambda e: canvas.xview_scroll(1, "units"))

            # Bind récursivement sur tous les enfants
            for child in widget.winfo_children():
                bind_to_all_children(child)

        # Appliquer le bind à tous les widgets
        bind_to_all_children(widget)

    def setup_styles(self):
        """Configurer les styles visuels"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Style pour les notebooks
        self.style.configure('Custom.TNotebook',
                             background='#34495e',
                             borderwidth=0)
        self.style.configure('Custom.TNotebook.Tab',
                             background='#34495e',
                             foreground='white',
                             # Padding réduit pour économiser l'espace
                             padding=[15, 8],
                             focuscolor='none')
        self.style.map('Custom.TNotebook.Tab',
                       background=[('selected', '#3498db'),
                                   ('active', '#5dade2')])

        # Style pour les frames
        self.style.configure('Card.TLabelFrame',
                             background='#ecf0f1',
                             borderwidth=2,
                             relief='raised')

        # Style pour les boutons - adaptatif
        self.style.configure('Action.TButton',
                             background='#3498db',
                             foreground='white',
                             borderwidth=0,
                             focuscolor='none',
                             padding=[10, 5])
        self.style.map('Action.TButton',
                       background=[('active', '#2980b9')])

        self.style.configure('Success.TButton',
                             background='#27ae60',
                             foreground='white',
                             borderwidth=0,
                             focuscolor='none',
                             padding=[10, 5])
        self.style.map('Success.TButton',
                       background=[('active', '#219a52')])

        self.style.configure('Danger.TButton',
                             background='#e74c3c',
                             foreground='white',
                             borderwidth=0,
                             focuscolor='none',
                             padding=[10, 5])
        self.style.map('Danger.TButton',
                       background=[('active', '#c0392b')])

    def setup_ui(self):
        """Configurer l'interface utilisateur responsive"""
        # Frame principal - COMPLÈTEMENT responsive
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.grid(row=0, column=0, sticky='nsew',
                        padx=8, pady=8)  # Padding réduit
        # Le notebook prend tout l'espace vertical
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)  # Largeur complète

        # En-tête avec titre stylisé - hauteur adaptative
        header_frame = tk.Frame(main_frame, bg='#34495e')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        header_frame.grid_columnconfigure(0, weight=1)

        # Titre principal - taille adaptative
        self.title_label = tk.Label(header_frame,
                                    text="🏀 SYSTÈME DE GESTION NBA",
                                    # Taille réduite par défaut
                                    font=('Arial', 22, 'bold'),
                                    fg='white',
                                    bg='#34495e')
        self.title_label.grid(row=0, column=0, pady=(8, 0))

        # Sous-titre - taille adaptative
        self.subtitle_label = tk.Label(header_frame,
                                       text="Gestion complète des équipes, joueurs et statistiques",
                                       # Taille réduite par défaut
                                       font=('Arial', 11),
                                       fg='#bdc3c7',
                                       bg='#34495e')
        self.subtitle_label.grid(row=1, column=0, pady=(0, 8))

        # Barre d'outils - compacte
        toolbar_frame = tk.Frame(main_frame, bg='#34495e')
        toolbar_frame.grid(row=1, column=0, sticky='ew', pady=(0, 8))

        # Boutons de la barre d'outils - disposition horizontale responsive
        buttons_container = tk.Frame(toolbar_frame, bg='#34495e')
        buttons_container.pack(expand=True)

        ttk.Button(buttons_container, text="🔄 Actualiser",
                   style='Action.TButton',
                   command=self.actualiser_tout).pack(side=tk.LEFT, padx=3, pady=6)

        ttk.Button(buttons_container, text="⚠️ Vérifier",
                   style='Danger.TButton',
                   command=self.verifier_coherence).pack(side=tk.LEFT, padx=3, pady=6)

        ttk.Button(buttons_container, text="💾 Sauvegarder",
                   style='Success.TButton',
                   command=self.sauvegarder_donnees).pack(side=tk.LEFT, padx=3, pady=6)

        ttk.Button(buttons_container, text="📁 Charger",
                   style='Action.TButton',
                   command=self.charger_donnees).pack(side=tk.LEFT, padx=3, pady=6)

        # Notebook pour les onglets - prend tout l'espace disponible
        self.notebook = ttk.Notebook(main_frame, style='Custom.TNotebook')
        # NSEW pour expansion complète
        self.notebook.grid(row=2, column=0, sticky='nsew')

        # Créer les onglets
        self.create_equipes_tab()
        self.create_joueurs_tab()
        self.create_matchs_tab()
        self.create_statistiques_tab()
        self.create_analyse_tab()

        # Appliquer l'ajustement initial après un court délai
        self.root.after(100, self.adjust_ui_scaling)

    def create_scrollable_frame(self, parent):
        """Créer un frame scrollable responsive"""
        # Container principal - occupe tout l'espace
        container = tk.Frame(parent, bg='#ecf0f1')

        # Canvas principal avec scrollbars
        main_canvas = tk.Canvas(container, bg='#ecf0f1', highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=main_canvas.yview)
        h_scrollbar = ttk.Scrollbar(
            container, orient="horizontal", command=main_canvas.xview)

        # Frame scrollable
        scrollable_frame = tk.Frame(main_canvas, bg='#ecf0f1')

        # Configuration du scrolling
        def configure_scroll_region(event=None):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        canvas_window = main_canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw")

        # Fonction pour ajuster la largeur du frame interne
        def configure_canvas(event):
            canvas_width = event.width
            main_canvas.itemconfig(canvas_window, width=canvas_width)

        main_canvas.bind('<Configure>', configure_canvas)
        main_canvas.configure(yscrollcommand=v_scrollbar.set,
                              xscrollcommand=h_scrollbar.set)

        # Placement des éléments - RESPONSIVE
        main_canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # Configuration responsive - CRUCIAL
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Bind pour la molette
        self.bind_mousewheel(container, main_canvas)
        self.bind_mousewheel(scrollable_frame, main_canvas)

        return container, scrollable_frame

    def create_equipes_tab(self):
        """Créer l'onglet de gestion des équipes responsive"""
        equipes_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(equipes_frame, text="🏀 Équipes")

        # Configuration responsive
        equipes_frame.grid_rowconfigure(0, weight=1)
        equipes_frame.grid_columnconfigure(0, weight=1)

        # Container scrollable
        container, scrollable_frame = self.create_scrollable_frame(
            equipes_frame)
        container.grid(row=0, column=0, sticky='nsew')

        # Section ajout d'équipe - compacte
        add_frame = tk.LabelFrame(scrollable_frame, text="➕ Ajouter une équipe",
                                  font=('Arial', 11, 'bold'),
                                  bg='white', fg='#2c3e50',
                                  padx=15, pady=10)
        add_frame.pack(fill=tk.X, padx=8, pady=4)

        # Layout horizontal responsive pour les champs
        input_frame = tk.Frame(add_frame, bg='white')
        input_frame.pack(fill=tk.X)
        input_frame.grid_columnconfigure((1, 3), weight=1)

        tk.Label(input_frame, text="Nom:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=0, sticky='w', padx=4, pady=4)
        self.equipe_nom_var = tk.StringVar()
        nom_entry = tk.Entry(input_frame, textvariable=self.equipe_nom_var,
                             font=('Arial', 9), relief='solid', bd=1)
        nom_entry.grid(row=0, column=1, padx=8, pady=4, sticky='ew')

        tk.Label(input_frame, text="Ville:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=2, sticky='w', padx=4, pady=4)
        self.equipe_ville_var = tk.StringVar()
        ville_entry = tk.Entry(input_frame, textvariable=self.equipe_ville_var,
                               font=('Arial', 9), relief='solid', bd=1)
        ville_entry.grid(row=0, column=3, padx=8, pady=4, sticky='ew')

        ttk.Button(input_frame, text="➕ Ajouter",
                   style='Success.TButton',
                   command=self.ajouter_equipe).grid(row=0, column=4, padx=8, pady=4)

        # Section liste des équipes
        list_frame = tk.LabelFrame(scrollable_frame, text="📋 Liste des équipes",
                                   font=('Arial', 11, 'bold'),
                                   bg='white', fg='#2c3e50',
                                   padx=15, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Treeview container responsive
        tree_container = tk.Frame(list_frame, bg='white')
        tree_container.pack(fill=tk.BOTH, expand=True)
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        columns = ('Nom', 'Ville', 'V', 'D', '%',
                   'J', 'Statut')  # Colonnes abrégées
        self.equipes_tree = ttk.Treeview(
            tree_container, columns=columns, show='headings', height=5)

        # Configuration des colonnes adaptatives
        column_widths = {'Nom': 120, 'Ville': 100, 'V': 50, 'D': 50,
                         '%': 60, 'J': 40, 'Statut': 80}

        for col in columns:
            self.equipes_tree.heading(col, text=col)
            self.equipes_tree.column(col, width=column_widths.get(col, 80),
                                     anchor='center' if col in ['V', 'D', 'J', '%'] else 'w')

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.VERTICAL, command=self.equipes_tree.yview)
        h_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.HORIZONTAL, command=self.equipes_tree.xview)
        self.equipes_tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.equipes_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # Bind molette
        self.bind_mousewheel(self.equipes_tree, self.equipes_tree)

        # Boutons d'action compacts
        buttons_frame = tk.Frame(list_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=8)

        ttk.Button(buttons_frame, text="🔄 Actualiser",
                   style='Action.TButton',
                   command=self.actualiser_equipes).pack(side=tk.LEFT, padx=3)
        ttk.Button(buttons_frame, text="👁️ Détails",
                   style='Action.TButton',
                   command=self.voir_details_equipe).pack(side=tk.LEFT, padx=3)
        ttk.Button(buttons_frame, text="📊 Stats",
                   style='Action.TButton',
                   command=self.voir_stats_equipe).pack(side=tk.LEFT, padx=3)

    def create_joueurs_tab(self):
        """Créer l'onglet de gestion des joueurs responsive"""
        joueurs_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(joueurs_frame, text="👤 Joueurs")

        # Configuration responsive
        joueurs_frame.grid_rowconfigure(0, weight=1)
        joueurs_frame.grid_columnconfigure(0, weight=1)

        # Container scrollable
        container, scrollable_frame = self.create_scrollable_frame(
            joueurs_frame)
        container.grid(row=0, column=0, sticky='nsew')

        # Section ajout de joueur - layout compact
        add_frame = tk.LabelFrame(scrollable_frame, text="➕ Ajouter un joueur",
                                  font=('Arial', 11, 'bold'),
                                  bg='white', fg='#2c3e50',
                                  padx=15, pady=10)
        add_frame.pack(fill=tk.X, padx=8, pady=4)

        # Layout en 2 lignes pour économiser l'espace vertical
        line1_frame = tk.Frame(add_frame, bg='white')
        line1_frame.pack(fill=tk.X, pady=3)
        line1_frame.grid_columnconfigure((1, 3, 5), weight=1)

        tk.Label(line1_frame, text="Nom:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=0, sticky='w', padx=3)
        self.joueur_nom_var = tk.StringVar()
        tk.Entry(line1_frame, textvariable=self.joueur_nom_var,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=1, padx=5, sticky='ew')

        tk.Label(line1_frame, text="Origine:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=2, sticky='w', padx=3)
        self.joueur_origine_var = tk.StringVar()
        tk.Entry(line1_frame, textvariable=self.joueur_origine_var,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=3, padx=5, sticky='ew')

        tk.Label(line1_frame, text="Année:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=4, sticky='w', padx=3)
        self.joueur_annee_var = tk.StringVar()
        tk.Entry(line1_frame, textvariable=self.joueur_annee_var, width=6,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=5, padx=5, sticky='ew')

        # Deuxième ligne
        line2_frame = tk.Frame(add_frame, bg='white')
        line2_frame.pack(fill=tk.X, pady=3)
        line2_frame.grid_columnconfigure((1, 3), weight=1)

        tk.Label(line2_frame, text="Équipe:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=0, sticky='w', padx=3)
        self.joueur_equipe_var = tk.StringVar()
        self.joueur_equipe_combo = ttk.Combobox(
            line2_frame, textvariable=self.joueur_equipe_var, font=('Arial', 9))
        self.joueur_equipe_combo.grid(row=0, column=1, padx=5, sticky='ew')

        tk.Label(line2_frame, text="Poste:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=2, sticky='w', padx=3)
        self.joueur_poste_var = tk.StringVar()
        poste_combo = ttk.Combobox(
            line2_frame, textvariable=self.joueur_poste_var, font=('Arial', 9))
        poste_combo['values'] = [poste.value for poste in PosteJoueur]
        poste_combo.grid(row=0, column=3, padx=5, sticky='ew')

        ttk.Button(line2_frame, text="➕ Ajouter",
                   style='Success.TButton',
                   command=self.ajouter_joueur).grid(row=0, column=4, padx=8)

        # Section transfert - compacte
        transfer_frame = tk.LabelFrame(scrollable_frame, text="🔄 Transférer",
                                       font=('Arial', 11, 'bold'),
                                       bg='white', fg='#2c3e50',
                                       padx=15, pady=8)
        transfer_frame.pack(fill=tk.X, padx=8, pady=4)

        transfer_input = tk.Frame(transfer_frame, bg='white')
        transfer_input.pack(fill=tk.X)
        transfer_input.grid_columnconfigure((1, 3), weight=1)

        tk.Label(transfer_input, text="Joueur:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=0, sticky='w', padx=3)
        self.transfer_joueur_var = tk.StringVar()
        self.transfer_joueur_combo = ttk.Combobox(
            transfer_input, textvariable=self.transfer_joueur_var, font=('Arial', 9))
        self.transfer_joueur_combo.grid(row=0, column=1, padx=5, sticky='ew')

        tk.Label(transfer_input, text="Vers:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=2, sticky='w', padx=3)
        self.transfer_equipe_var = tk.StringVar()
        self.transfer_equipe_combo = ttk.Combobox(
            transfer_input, textvariable=self.transfer_equipe_var, font=('Arial', 9))
        self.transfer_equipe_combo.grid(row=0, column=3, padx=5, sticky='ew')

        ttk.Button(transfer_input, text="🔄 OK",
                   style='Action.TButton',
                   command=self.transferer_joueur).grid(row=0, column=4, padx=8)

        # Section statistiques - compacte
        stats_frame = tk.LabelFrame(scrollable_frame, text="📊 Statistiques",
                                    font=('Arial', 11, 'bold'),
                                    bg='white', fg='#2c3e50',
                                    padx=15, pady=8)
        stats_frame.pack(fill=tk.X, padx=8, pady=4)

        # Deux lignes compactes
        stats_line1 = tk.Frame(stats_frame, bg='white')
        stats_line1.pack(fill=tk.X, pady=2)
        stats_line1.grid_columnconfigure((1, 3, 5), weight=1)

        tk.Label(stats_line1, text="Joueur:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=0, sticky='w', padx=3)
        self.stats_joueur_var = tk.StringVar()
        self.stats_joueur_combo = ttk.Combobox(
            stats_line1, textvariable=self.stats_joueur_var, font=('Arial', 9))
        self.stats_joueur_combo.grid(row=0, column=1, padx=5, sticky='ew')

        tk.Label(stats_line1, text="Temps:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=2, sticky='w', padx=3)
        self.stats_temps_var = tk.StringVar()
        tk.Entry(stats_line1, textvariable=self.stats_temps_var, width=6,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=3, padx=5, sticky='ew')

        tk.Label(stats_line1, text="Points:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=4, sticky='w', padx=3)
        self.stats_points_var = tk.StringVar()
        tk.Entry(stats_line1, textvariable=self.stats_points_var, width=6,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=5, padx=5, sticky='ew')

        stats_line2 = tk.Frame(stats_frame, bg='white')
        stats_line2.pack(fill=tk.X, pady=2)
        stats_line2.grid_columnconfigure((1, 3), weight=1)

        tk.Label(stats_line2, text="Passes:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=0, sticky='w', padx=3)
        self.stats_passes_var = tk.StringVar()
        tk.Entry(stats_line2, textvariable=self.stats_passes_var, width=6,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=1, padx=5, sticky='ew')

        tk.Label(stats_line2, text="Rebonds:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=2, sticky='w', padx=3)
        self.stats_rebonds_var = tk.StringVar()
        tk.Entry(stats_line2, textvariable=self.stats_rebonds_var, width=6,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=3, padx=5, sticky='ew')

        ttk.Button(stats_line2, text="📊 Ajouter",
                   style='Success.TButton',
                   command=self.ajouter_statistiques).grid(row=0, column=4, padx=8)

        # Liste des joueurs
        list_frame = tk.LabelFrame(scrollable_frame, text="👥 Liste des joueurs",
                                   font=('Arial', 11, 'bold'),
                                   bg='white', fg='#2c3e50',
                                   padx=15, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tree_container = tk.Frame(list_frame, bg='white')
        tree_container.pack(fill=tk.BOTH, expand=True)
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        columns = ('Nom', 'Équipe', 'Poste', 'Origine',
                   'Année', 'M', 'Pts', 'Eff')
        self.joueurs_tree = ttk.Treeview(
            tree_container, columns=columns, show='headings', height=5)

        # Colonnes adaptatives
        column_widths = {'Nom': 100, 'Équipe': 80, 'Poste': 60, 'Origine': 60,
                         'Année': 50, 'M': 30, 'Pts': 40, 'Eff': 40}

        for col in columns:
            self.joueurs_tree.heading(col, text=col)
            self.joueurs_tree.column(col, width=column_widths.get(col, 60),
                                     anchor='center' if col in ['M', 'Pts', 'Eff', 'Année'] else 'w')

        v_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.VERTICAL, command=self.joueurs_tree.yview)
        h_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.HORIZONTAL, command=self.joueurs_tree.xview)
        self.joueurs_tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.joueurs_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        self.bind_mousewheel(self.joueurs_tree, self.joueurs_tree)

        # Boutons
        buttons_frame = tk.Frame(list_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=8)

        ttk.Button(buttons_frame, text="🔄 Actualiser",
                   style='Action.TButton',
                   command=self.actualiser_joueurs).pack(side=tk.LEFT, padx=3)
        ttk.Button(buttons_frame, text="📊 Stats",
                   style='Action.TButton',
                   command=self.voir_stats_joueur).pack(side=tk.LEFT, padx=3)

    def create_matchs_tab(self):
        """Créer l'onglet de gestion des matchs responsive"""
        matchs_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(matchs_frame, text="⚡ Matchs")

        # Configuration responsive
        matchs_frame.grid_rowconfigure(0, weight=1)
        matchs_frame.grid_columnconfigure(0, weight=1)

        # Container scrollable
        container, scrollable_frame = self.create_scrollable_frame(
            matchs_frame)
        container.grid(row=0, column=0, sticky='nsew')

        # Section ajout de match - compacte
        add_frame = tk.LabelFrame(scrollable_frame, text="➕ Ajouter un match",
                                  font=('Arial', 11, 'bold'),
                                  bg='white', fg='#2c3e50',
                                  padx=15, pady=10)
        add_frame.pack(fill=tk.X, padx=8, pady=4)

        # Layout en 2 lignes compactes
        line1_frame = tk.Frame(add_frame, bg='white')
        line1_frame.pack(fill=tk.X, pady=3)
        line1_frame.grid_columnconfigure((1, 3), weight=1)

        tk.Label(line1_frame, text="Domicile:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=0, sticky='w', padx=3)
        self.match_domicile_var = tk.StringVar()
        self.match_domicile_combo = ttk.Combobox(
            line1_frame, textvariable=self.match_domicile_var, font=('Arial', 9))
        self.match_domicile_combo.grid(row=0, column=1, padx=5, sticky='ew')

        tk.Label(line1_frame, text="Score:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=2, sticky='w', padx=3)
        self.match_score_dom_var = tk.StringVar()
        tk.Entry(line1_frame, textvariable=self.match_score_dom_var, width=6,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=3, padx=5, sticky='ew')

        line2_frame = tk.Frame(add_frame, bg='white')
        line2_frame.pack(fill=tk.X, pady=3)
        line2_frame.grid_columnconfigure((1, 3, 5), weight=1)

        tk.Label(line2_frame, text="Extérieur:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=0, sticky='w', padx=3)
        self.match_exterieur_var = tk.StringVar()
        self.match_exterieur_combo = ttk.Combobox(
            line2_frame, textvariable=self.match_exterieur_var, font=('Arial', 9))
        self.match_exterieur_combo.grid(row=0, column=1, padx=5, sticky='ew')

        tk.Label(line2_frame, text="Score:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=2, sticky='w', padx=3)
        self.match_score_ext_var = tk.StringVar()
        tk.Entry(line2_frame, textvariable=self.match_score_ext_var, width=6,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=3, padx=5, sticky='ew')

        tk.Label(line2_frame, text="Date:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=4, sticky='w', padx=3)
        self.match_date_var = tk.StringVar()
        self.match_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(line2_frame, textvariable=self.match_date_var, width=10,
                 font=('Arial', 9), relief='solid', bd=1).grid(row=0, column=5, padx=5, sticky='ew')

        ttk.Button(line2_frame, text="⚡ Ajouter",
                   style='Success.TButton',
                   command=self.ajouter_match).grid(row=0, column=6, padx=8)

        # Liste des matchs
        list_frame = tk.LabelFrame(scrollable_frame, text="📋 Historique des matchs",
                                   font=('Arial', 11, 'bold'),
                                   bg='white', fg='#2c3e50',
                                   padx=15, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tree_container = tk.Frame(list_frame, bg='white')
        tree_container.pack(fill=tk.BOTH, expand=True)
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        columns = ('Date', 'Domicile', 'S.D', 'S.E',
                   'Extérieur', 'Gagnant', 'Écart', 'Type')
        self.matchs_tree = ttk.Treeview(
            tree_container, columns=columns, show='headings', height=5)

        # Colonnes adaptatives
        column_widths = {'Date': 80, 'Domicile': 80, 'S.D': 35, 'S.E': 35,
                         'Extérieur': 80, 'Gagnant': 80, 'Écart': 40, 'Type': 60}

        for col in columns:
            self.matchs_tree.heading(col, text=col)
            self.matchs_tree.column(col, width=column_widths.get(col, 70),
                                    anchor='center' if col in ['S.D', 'S.E', 'Écart'] else 'w')

        v_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.VERTICAL, command=self.matchs_tree.yview)
        h_scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.HORIZONTAL, command=self.matchs_tree.xview)
        self.matchs_tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.matchs_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        self.bind_mousewheel(self.matchs_tree, self.matchs_tree)

        # Boutons
        buttons_frame = tk.Frame(list_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=8)

        ttk.Button(buttons_frame, text="🔄 Actualiser",
                   style='Action.TButton',
                   command=self.actualiser_matchs).pack(side=tk.LEFT, padx=3)
        ttk.Button(buttons_frame, text="📊 Analyser",
                   style='Action.TButton',
                   command=self.analyser_match).pack(side=tk.LEFT, padx=3)

    def create_statistiques_tab(self):
        """Créer l'onglet des statistiques responsive"""
        stats_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(stats_frame, text="📊 Statistiques")

        # Configuration responsive
        stats_frame.grid_rowconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(0, weight=1)

        # Container scrollable
        container, scrollable_frame = self.create_scrollable_frame(stats_frame)
        container.grid(row=0, column=0, sticky='nsew')

        # Frame pour les statistiques générales - plus compacte
        general_frame = tk.LabelFrame(scrollable_frame, text="📈 Statistiques générales",
                                      font=('Arial', 11, 'bold'),
                                      bg='white', fg='#2c3e50',
                                      padx=15, pady=10)
        general_frame.pack(fill=tk.X, padx=8, pady=4)

        self.stats_general_text = tk.Text(general_frame, height=6, width=80,
                                          font=('Courier', 9),
                                          bg='#f8f9fa', relief='solid', bd=1)
        self.stats_general_text.pack(fill=tk.X)

        # Container pour classement et top joueurs - côte à côte
        dual_container = tk.Frame(scrollable_frame, bg='#ecf0f1')
        dual_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Frame pour le classement
        classement_frame = tk.LabelFrame(dual_container, text="🏆 Classement",
                                         font=('Arial', 11, 'bold'),
                                         bg='white', fg='#2c3e50',
                                         padx=10, pady=8)
        classement_frame.pack(side=tk.LEFT, fill=tk.BOTH,
                              expand=True, padx=(0, 4))

        columns_classement = ('Pos', 'Équipe', 'V', 'D', '%')
        self.classement_tree = ttk.Treeview(
            classement_frame, columns=columns_classement, show='headings', height=5)

        # Colonnes plus compactes
        column_widths_class = {'Pos': 30,
                               'Équipe': 80, 'V': 30, 'D': 30, '%': 50}

        for col in columns_classement:
            self.classement_tree.heading(col, text=col)
            self.classement_tree.column(col, width=column_widths_class.get(col, 50),
                                        anchor='center' if col in ['Pos', 'V', 'D', '%'] else 'w')

        scrollbar_classement = ttk.Scrollbar(
            classement_frame, orient=tk.VERTICAL, command=self.classement_tree.yview)
        self.classement_tree.configure(yscrollcommand=scrollbar_classement.set)

        self.classement_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_classement.pack(side=tk.RIGHT, fill=tk.Y)

        self.bind_mousewheel(self.classement_tree, self.classement_tree)

        # Frame pour le top joueurs
        top_frame = tk.LabelFrame(dual_container, text="⭐ Top joueurs",
                                  font=('Arial', 11, 'bold'),
                                  bg='white', fg='#2c3e50',
                                  padx=10, pady=8)
        top_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(4, 0))

        # Sélection du critère - plus compacte
        critere_container = tk.Frame(top_frame, bg='white')
        critere_container.pack(fill=tk.X, pady=(0, 5))

        tk.Label(critere_container, text="Critère:", font=('Arial', 9, 'bold'),
                 bg='white').pack(side=tk.LEFT, padx=3)
        self.critere_var = tk.StringVar(value="points")
        critere_combo = ttk.Combobox(
            critere_container, textvariable=self.critere_var, width=12, font=('Arial', 9))
        critere_combo['values'] = [
            'points', 'passes', 'rebonds', 'efficacite_moyenne']
        critere_combo.pack(side=tk.LEFT, padx=3)

        ttk.Button(critere_container, text="🔄",
                   style='Action.TButton',
                   command=self.actualiser_top_joueurs).pack(side=tk.LEFT, padx=3)

        columns_top = ('Pos', 'Joueur', 'Équipe', 'Val')
        self.top_tree = ttk.Treeview(
            top_frame, columns=columns_top, show='headings', height=5)

        # Colonnes compactes
        column_widths_top = {'Pos': 30, 'Joueur': 70, 'Équipe': 60, 'Val': 40}

        for col in columns_top:
            self.top_tree.heading(col, text=col)
            self.top_tree.column(col, width=column_widths_top.get(col, 50),
                                 anchor='center' if col in ['Pos', 'Val'] else 'w')

        scrollbar_top = ttk.Scrollbar(
            top_frame, orient=tk.VERTICAL, command=self.top_tree.yview)
        self.top_tree.configure(yscrollcommand=scrollbar_top.set)

        self.top_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_top.pack(side=tk.RIGHT, fill=tk.Y)

        self.bind_mousewheel(self.top_tree, self.top_tree)

        # Bouton actualiser général
        update_button = ttk.Button(scrollable_frame, text="🔄 Actualiser toutes les statistiques",
                                   style='Success.TButton',
                                   command=self.actualiser_statistiques)
        update_button.pack(pady=15)

    def create_analyse_tab(self):
        """Créer l'onglet d'analyse responsive"""
        analyse_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(analyse_frame, text="🔍 Analyse")

        # Configuration responsive
        analyse_frame.grid_rowconfigure(0, weight=1)
        analyse_frame.grid_columnconfigure(0, weight=1)

        # Container scrollable
        container, scrollable_frame = self.create_scrollable_frame(
            analyse_frame)
        container.grid(row=0, column=0, sticky='nsew')

        # Section comparaison d'équipes - compacte
        compare_frame = tk.LabelFrame(scrollable_frame, text="⚖️ Comparaison d'équipes",
                                      font=('Arial', 11, 'bold'),
                                      bg='white', fg='#2c3e50',
                                      padx=15, pady=10)
        compare_frame.pack(fill=tk.X, padx=8, pady=4)

        compare_input = tk.Frame(compare_frame, bg='white')
        compare_input.pack(fill=tk.X, pady=3)
        compare_input.grid_columnconfigure((1, 3), weight=1)

        tk.Label(compare_input, text="Équipe 1:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=0, sticky='w', padx=3)
        self.compare_equipe1_var = tk.StringVar()
        self.compare_equipe1_combo = ttk.Combobox(
            compare_input, textvariable=self.compare_equipe1_var, font=('Arial', 9))
        self.compare_equipe1_combo.grid(row=0, column=1, padx=5, sticky='ew')

        tk.Label(compare_input, text="Équipe 2:", font=('Arial', 9, 'bold'),
                 bg='white').grid(row=0, column=2, sticky='w', padx=3)
        self.compare_equipe2_var = tk.StringVar()
        self.compare_equipe2_combo = ttk.Combobox(
            compare_input, textvariable=self.compare_equipe2_var, font=('Arial', 9))
        self.compare_equipe2_combo.grid(row=0, column=3, padx=5, sticky='ew')

        ttk.Button(compare_input, text="⚖️ Comparer",
                   style='Action.TButton',
                   command=self.comparer_equipes).grid(row=0, column=4, padx=8)

        self.comparaison_text = tk.Text(compare_frame, height=8, width=80,
                                        font=('Courier', 9),
                                        bg='#f8f9fa', relief='solid', bd=1)
        self.comparaison_text.pack(fill=tk.X, pady=8)

        # Section analyse de performances
        perf_frame = tk.LabelFrame(scrollable_frame, text="📈 Analyse de performances",
                                   font=('Arial', 11, 'bold'),
                                   bg='white', fg='#2c3e50',
                                   padx=15, pady=10)
        perf_frame.pack(fill=tk.X, padx=8, pady=4)

        perf_buttons = tk.Frame(perf_frame, bg='white')
        perf_buttons.pack(fill=tk.X, pady=3)

        ttk.Button(perf_buttons, text="📊 Tendances",
                   style='Action.TButton',
                   command=self.analyser_tendances).pack(side=tk.LEFT, padx=3)
        ttk.Button(perf_buttons, text="⭐ Top joueurs",
                   style='Action.TButton',
                   command=self.joueurs_en_forme).pack(side=tk.LEFT, padx=3)
        ttk.Button(perf_buttons, text="📉 Équipes faibles",
                   style='Danger.TButton',
                   command=self.equipes_en_difficulte).pack(side=tk.LEFT, padx=3)

        self.analyse_text = tk.Text(perf_frame, height=12, width=80,
                                    font=('Courier', 9),
                                    bg='#f8f9fa', relief='solid', bd=1)
        self.analyse_text.pack(fill=tk.X, pady=8)

    # =====================================
    # Méthodes pour les équipes améliorées
    # =====================================

    def ajouter_equipe(self):
        """Ajouter une nouvelle équipe avec validation améliorée"""
        nom = self.equipe_nom_var.get().strip()
        ville = self.equipe_ville_var.get().strip()

        if not nom or not ville:
            self.show_error_popup("Erreur de saisie",
                                  "Veuillez remplir tous les champs!")
            return

        # Validation des caractères
        if not nom.replace(' ', '').isalnum() or not ville.replace(' ', '').isalnum():
            self.show_error_popup("Erreur de validation",
                                  "Le nom et la ville ne doivent contenir que des lettres et chiffres!")
            return

        try:
            if self.nba_system:
                self.nba_system.ajouter_equipe(nom, ville)
                self.show_success_popup(
                    "Succès", f"Équipe {nom} ajoutée avec succès!")
                self.equipe_nom_var.set("")
                self.equipe_ville_var.set("")
                self.actualiser_equipes()
                self.actualiser_comboboxes()
            else:
                self.show_error_popup("Erreur", "Système NBA non initialisé!")
        except (ValueError, ValidationError) as e:
            self.show_error_popup("Erreur", str(e))

    def actualiser_equipes(self):
        """Actualiser la liste des équipes avec couleurs"""
        # Vider le treeview
        for item in self.equipes_tree.get_children():
            self.equipes_tree.delete(item)

        if not self.nba_system:
            return

        # Ajouter les équipes avec codes couleur
        for equipe in self.nba_system._equipes.values():
            pourcentage = equipe.calculer_pourcentage_victoires()

            # Déterminer le statut
            if equipe.victoires + equipe.defaites == 0:
                statut = "Inactif"
                tag = "inactive"
            elif pourcentage >= 60:
                statut = "Excellent"
                tag = "excellent"
            elif pourcentage >= 50:
                statut = "Bon"
                tag = "bon"
            else:
                statut = "Difficile"
                tag = "difficile"

            item = self.equipes_tree.insert('', 'end', values=(
                equipe.nom,
                equipe.ville,
                equipe.victoires,
                equipe.defaites,
                f"{pourcentage:.1f}%",
                len(equipe.joueurs),
                statut
            ), tags=(tag,))

        # Configuration des tags pour les couleurs
        self.equipes_tree.tag_configure("excellent", background="#d5f4e6")
        self.equipes_tree.tag_configure("bon", background="#fff3cd")
        self.equipes_tree.tag_configure("difficile", background="#f8d7da")
        self.equipes_tree.tag_configure("inactive", background="#e2e3e5")

    def voir_details_equipe(self):
        """Voir les détails d'une équipe avec interface améliorée"""
        selection = self.equipes_tree.selection()
        if not selection:
            self.show_warning_popup(
                "Attention", "Veuillez sélectionner une équipe!")
            return

        item = self.equipes_tree.item(selection[0])
        nom_equipe = item['values'][0]

        if self.nba_system:
            equipe = self.nba_system.rechercher_equipe(nom_equipe)
            if equipe:
                self.create_equipe_details_window(equipe)

    def voir_stats_equipe(self):
        """Voir les statistiques détaillées d'une équipe"""
        selection = self.equipes_tree.selection()
        if not selection:
            self.show_warning_popup(
                "Attention", "Veuillez sélectionner une équipe!")
            return

        item = self.equipes_tree.item(selection[0])
        nom_equipe = item['values'][0]

        if self.nba_system:
            equipe = self.nba_system.rechercher_equipe(nom_equipe)
            if equipe:
                self.create_equipe_stats_window(equipe)

    # =====================================
    # Méthodes pour les joueurs améliorées
    # =====================================

    def ajouter_joueur(self):
        """Ajouter un nouveau joueur avec validation améliorée"""
        nom = self.joueur_nom_var.get().strip()
        origine = self.joueur_origine_var.get().strip()
        annee_str = self.joueur_annee_var.get().strip()
        equipe_nom = self.joueur_equipe_var.get().strip()
        poste = self.joueur_poste_var.get().strip()

        if not all([nom, origine, annee_str, equipe_nom, poste]):
            self.show_error_popup("Erreur de saisie",
                                  "Veuillez remplir tous les champs!")
            return

        try:
            annee = int(annee_str)
            if annee < 1946 or annee > datetime.now().year:
                raise ValueError("Année invalide")

            if self.nba_system:
                self.nba_system.ajouter_joueur_a_equipe(
                    equipe_nom, nom, origine, annee, poste)
                self.show_success_popup(
                    "Succès", f"Joueur {nom} ajouté à {equipe_nom}!")

                # Vider les champs
                self.joueur_nom_var.set("")
                self.joueur_origine_var.set("")
                self.joueur_annee_var.set("")
                self.joueur_equipe_var.set("")
                self.joueur_poste_var.set("")

                self.actualiser_joueurs()
                self.actualiser_comboboxes()
            else:
                self.show_error_popup("Erreur", "Système NBA non initialisé!")
        except (ValueError, ValidationError) as e:
            self.show_error_popup("Erreur", str(e))

    def transferer_joueur(self):
        """Transférer un joueur avec confirmation"""
        nom_joueur = self.transfer_joueur_var.get().strip()
        nouvelle_equipe = self.transfer_equipe_var.get().strip()

        if not nom_joueur or not nouvelle_equipe:
            self.show_error_popup("Erreur de saisie",
                                  "Veuillez remplir tous les champs!")
            return

        if not self.nba_system:
            self.show_error_popup("Erreur", "Système NBA non initialisé!")
            return

        # Confirmation du transfert
        joueur = self.nba_system.rechercher_joueur(nom_joueur)
        ancienne_equipe = joueur.equipe.nom if joueur and joueur.equipe else "Aucune"

        if messagebox.askyesno("Confirmation",
                               f"Confirmer le transfert de {nom_joueur}\n"
                               f"De: {ancienne_equipe}\n"
                               f"Vers: {nouvelle_equipe}"):
            try:
                self.nba_system.transferer_joueur(nom_joueur, nouvelle_equipe)
                self.show_success_popup(
                    "Succès", f"{nom_joueur} transféré vers {nouvelle_equipe}!")

                self.transfer_joueur_var.set("")
                self.transfer_equipe_var.set("")

                self.actualiser_joueurs()
                self.actualiser_equipes()
            except (ValueError, ValidationError) as e:
                self.show_error_popup("Erreur", str(e))

    def ajouter_statistiques(self):
        """Ajouter des statistiques avec validation améliorée"""
        nom_joueur = self.stats_joueur_var.get().strip()

        if not nom_joueur:
            self.show_error_popup("Erreur de saisie",
                                  "Veuillez sélectionner un joueur!")
            return

        try:
            temps = float(self.stats_temps_var.get())
            points = int(self.stats_points_var.get())
            passes = int(self.stats_passes_var.get())
            rebonds = int(self.stats_rebonds_var.get())

            # Validation des valeurs
            if not (0 <= temps <= 48):
                raise ValueError(
                    "Le temps de jeu doit être entre 0 et 48 minutes")
            if points < 0 or passes < 0 or rebonds < 0:
                raise ValueError(
                    "Les statistiques ne peuvent pas être négatives")

            if self.nba_system:
                joueur = self.nba_system.rechercher_joueur(nom_joueur)
                if joueur:
                    joueur.ajouter_statistiques(temps, points, passes, rebonds)
                    self.show_success_popup(
                        "Succès", f"Statistiques ajoutées pour {nom_joueur}!")

                    # Vider les champs
                    self.stats_temps_var.set("")
                    self.stats_points_var.set("")
                    self.stats_passes_var.set("")
                    self.stats_rebonds_var.set("")

                    self.actualiser_joueurs()
                else:
                    self.show_error_popup("Erreur", "Joueur non trouvé!")
            else:
                self.show_error_popup("Erreur", "Système NBA non initialisé!")

        except ValueError as e:
            self.show_error_popup("Erreur", f"Valeurs invalides: {e}")

    def actualiser_joueurs(self):
        """Actualiser la liste des joueurs avec couleurs"""
        # Vider le treeview
        for item in self.joueurs_tree.get_children():
            self.joueurs_tree.delete(item)

        if not self.nba_system:
            return

        # Ajouter les joueurs avec codes couleur
        for joueur in self.nba_system._joueurs_index.values():
            moyennes = joueur.calculer_moyennes()
            equipe_nom = joueur.equipe.nom if joueur.equipe else "Libre"

            if moyennes:
                matchs = moyennes['matchs_joues']
                points_match = f"{moyennes['points']:.1f}"
                efficacite = f"{moyennes['efficacite_moyenne']:.2f}"

                # Déterminer le tag selon les performances
                if moyennes['points'] >= 20:
                    tag = "star"
                elif moyennes['points'] >= 10:
                    tag = "good"
                else:
                    tag = "normal"
            else:
                matchs = 0
                points_match = "0.0"
                efficacite = "0.00"
                tag = "inactive"

            self.joueurs_tree.insert('', 'end', values=(
                joueur.nom,
                equipe_nom,
                joueur.poste.value,
                joueur.origine,
                joueur.annee_debut,
                matchs,
                points_match,
                efficacite
            ), tags=(tag,))

        # Configuration des tags
        self.joueurs_tree.tag_configure("star", background="#fff2cc")
        self.joueurs_tree.tag_configure("good", background="#e2f0d9")
        self.joueurs_tree.tag_configure("normal", background="#f2f2f2")
        self.joueurs_tree.tag_configure("inactive", background="#e2e3e5")

    def voir_stats_joueur(self):
        """Voir les statistiques détaillées d'un joueur"""
        selection = self.joueurs_tree.selection()
        if not selection:
            self.show_warning_popup(
                "Attention", "Veuillez sélectionner un joueur!")
            return

        item = self.joueurs_tree.item(selection[0])
        nom_joueur = item['values'][0]

        if self.nba_system:
            joueur = self.nba_system.rechercher_joueur(nom_joueur)
            if joueur:
                self.create_joueur_stats_window(joueur)

    # =====================================
    # Méthodes pour les matchs améliorées
    # =====================================

    def ajouter_match(self):
        """Ajouter un nouveau match avec validation améliorée"""
        equipe_dom = self.match_domicile_var.get().strip()
        equipe_ext = self.match_exterieur_var.get().strip()
        score_dom_str = self.match_score_dom_var.get().strip()
        score_ext_str = self.match_score_ext_var.get().strip()
        date_str = self.match_date_var.get().strip()

        if not all([equipe_dom, equipe_ext, score_dom_str, score_ext_str, date_str]):
            self.show_error_popup("Erreur de saisie",
                                  "Veuillez remplir tous les champs!")
            return

        if equipe_dom == equipe_ext:
            self.show_error_popup(
                "Erreur de validation", "Une équipe ne peut pas jouer contre elle-même!")
            return

        try:
            score_dom = int(score_dom_str)
            score_ext = int(score_ext_str)

            if score_dom < 0 or score_ext < 0:
                raise ValueError("Les scores ne peuvent pas être négatifs")

            self.nba_system.ajouter_match(
                equipe_dom, equipe_ext, score_dom, score_ext, date_str)

            gagnant = equipe_dom if score_dom > score_ext else equipe_ext if score_ext > score_dom else "Égalité"
            self.show_success_popup("Succès",
                                    f"Match ajouté: {equipe_dom} {score_dom} - {score_ext} {equipe_ext}\nGagnant: {gagnant}")

            # Vider les champs
            self.match_domicile_var.set("")
            self.match_exterieur_var.set("")
            self.match_score_dom_var.set("")
            self.match_score_ext_var.set("")
            self.match_date_var.set(datetime.now().strftime("%Y-%m-%d"))

            self.actualiser_matchs()
            self.actualiser_equipes()

        except (ValueError, ValidationError) as e:
            self.show_error_popup("Erreur", str(e))

    def actualiser_matchs(self):
        """Actualiser la liste des matchs avec informations détaillées"""
        # Vider le treeview
        for item in self.matchs_tree.get_children():
            self.matchs_tree.delete(item)

        # Ajouter les matchs (triés par date)
        matchs_tries = sorted(self.nba_system._matchs,
                              key=lambda m: m.date, reverse=True)

        for match in matchs_tries:
            gagnant = match.get_equipe_gagnante()
            gagnant_nom = gagnant.nom if gagnant else "Égalité"
            ecart = match.get_ecart_points()

            # Déterminer le type de match
            if ecart == 0:
                type_match = "Égalité"
                tag = "egalite"
            elif ecart <= 5:
                type_match = "Serré"
                tag = "serre"
            elif ecart <= 15:
                type_match = "Normal"
                tag = "normal"
            else:
                type_match = "Domination"
                tag = "domination"

            self.matchs_tree.insert('', 'end', values=(
                match.date.strftime('%Y-%m-%d'),
                match.equipe_domicile.nom,
                match.score_domicile,
                match.score_exterieur,
                match.equipe_exterieur.nom,
                gagnant_nom,
                ecart,
                type_match
            ), tags=(tag,))

        # Configuration des tags
        self.matchs_tree.tag_configure("serre", background="#fff3cd")
        self.matchs_tree.tag_configure("normal", background="#f2f2f2")
        self.matchs_tree.tag_configure("domination", background="#d1ecf1")
        self.matchs_tree.tag_configure("egalite", background="#d5f4e6")

    def analyser_match(self):
        """Analyser un match sélectionné"""
        selection = self.matchs_tree.selection()
        if not selection:
            self.show_warning_popup(
                "Attention", "Veuillez sélectionner un match!")
            return

        item = self.matchs_tree.item(selection[0])
        values = item['values']

        # Trouver le match correspondant
        date_str = values[0]
        equipe_dom = values[1]
        equipe_ext = values[4]

        for match in self.nba_system._matchs:
            if (match.date.strftime('%Y-%m-%d') == date_str and
                    match.equipe_domicile.nom == equipe_dom and
                    match.equipe_exterieur.nom == equipe_ext):
                self.create_match_analysis_window(match)
                break

    # =====================================
    # Méthodes pour les statistiques améliorées
    # =====================================

    def actualiser_statistiques(self):
        """Actualiser toutes les statistiques avec animations"""
        self.actualiser_stats_generales()
        self.actualiser_classement()
        self.actualiser_top_joueurs()
        self.show_info_popup(
            "Information", "Toutes les statistiques ont été actualisées!")

    def actualiser_stats_generales(self):
        """Actualiser les statistiques générales avec plus de détails"""
        stats = self.nba_system.obtenir_statistiques_generales()

        texte = "=" * 60 + "\n"
        texte += "🏀 STATISTIQUES GÉNÉRALES DU SYSTÈME NBA\n"
        texte += "=" * 60 + "\n\n"

        texte += f"📊 ÉQUIPES:\n"
        texte += f"   • Total: {stats['equipes_total']} équipes enregistrées\n"
        texte += f"   • Actives: {stats['equipes_actives']} équipes avec des matchs\n"
        texte += f"   • Inactives: {stats['equipes_total'] - stats['equipes_actives']} équipes sans match\n\n"

        texte += f"👤 JOUEURS:\n"
        texte += f"   • Total: {stats['joueurs_total']} joueurs enregistrés\n"
        texte += f"   • Avec statistiques: {stats['joueurs_actifs']} joueurs actifs\n"
        texte += f"   • Sans statistiques: {stats['joueurs_total'] - stats['joueurs_actifs']} joueurs inactifs\n\n"

        texte += f"⚡ MATCHS:\n"
        texte += f"   • Total disputés: {stats['matchs_total']} matchs\n"

        if stats['matchs_total'] > 0:
            # Calculs avancés
            total_points = 0
            matchs_serres = 0

            for match in self.nba_system._matchs:
                total_points += match.score_domicile + match.score_exterieur
                if match.est_match_serre():
                    matchs_serres += 1

            moyenne_points = total_points / stats['matchs_total']
            pourcentage_serres = (matchs_serres / stats['matchs_total']) * 100

            texte += f"   • Points moyens par match: {moyenne_points:.1f} pts\n"
            texte += f"   • Matchs serrés (≤5 pts): {matchs_serres} ({pourcentage_serres:.1f}%)\n"

            # Équipe la plus performante
            classement = self.nba_system.obtenir_classement()
            if classement:
                meilleure = classement[0]
                texte += f"\n🏆 MEILLEURE ÉQUIPE:\n"
                texte += f"   • {meilleure.nom} - {meilleure.victoires}V/{meilleure.defaites}D "
                texte += f"({meilleure.calculer_pourcentage_victoires():.1f}%)\n"

        texte += "\n" + "=" * 60

        self.stats_general_text.config(state=tk.NORMAL)
        self.stats_general_text.delete(1.0, tk.END)
        self.stats_general_text.insert(tk.END, texte)
        self.stats_general_text.config(state=tk.DISABLED)

    def actualiser_classement(self):
        """Actualiser le classement avec médailles"""
        # Vider le treeview
        for item in self.classement_tree.get_children():
            self.classement_tree.delete(item)

        classement = self.nba_system.obtenir_classement()

        for i, equipe in enumerate(classement, 1):
            pourcentage = equipe.calculer_pourcentage_victoires()

            # Déterminer le tag selon la position
            if i == 1:
                tag = "first"
            elif i == 2:
                tag = "second"
            elif i == 3:
                tag = "third"
            else:
                tag = "other"

            # Ajouter médaille pour le podium
            position_text = f"🥇 {i}" if i == 1 else f"🥈 {i}" if i == 2 else f"🥉 {i}" if i == 3 else str(
                i)

            self.classement_tree.insert('', 'end', values=(
                position_text,
                equipe.nom,
                equipe.victoires,
                equipe.defaites,
                f"{pourcentage:.1f}%"
            ), tags=(tag,))

        # Configuration des tags
        self.classement_tree.tag_configure("first", background="#ffd700")
        self.classement_tree.tag_configure("second", background="#c0c0c0")
        self.classement_tree.tag_configure("third", background="#cd7f32")
        self.classement_tree.tag_configure("other", background="#f2f2f2")

    def actualiser_top_joueurs(self):
        """Actualiser le top des joueurs avec étoiles"""
        # Vider le treeview
        for item in self.top_tree.get_children():
            self.top_tree.delete(item)

        critere = self.critere_var.get()
        top_joueurs = self.nba_system.obtenir_top_joueurs(critere, 10)

        for i, (joueur, moyennes) in enumerate(top_joueurs, 1):
            valeur = moyennes[critere]
            equipe_nom = joueur.equipe.nom if joueur.equipe else "Libre"

            # Déterminer le tag selon la position
            if i <= 3:
                tag = "top3"
                position_text = f"⭐ {i}"
            else:
                tag = "other"
                position_text = str(i)

            self.top_tree.insert('', 'end', values=(
                position_text,
                joueur.nom,
                equipe_nom,
                f"{valeur:.1f}"
            ), tags=(tag,))

        # Configuration des tags
        self.top_tree.tag_configure("top3", background="#fff2cc")
        self.top_tree.tag_configure("other", background="#f2f2f2")

    # =====================================
    # Méthodes d'analyse avancée
    # =====================================

    def comparer_equipes(self):
        """Comparer deux équipes"""
        equipe1_nom = self.compare_equipe1_var.get().strip()
        equipe2_nom = self.compare_equipe2_var.get().strip()

        if not equipe1_nom or not equipe2_nom:
            self.show_error_popup(
                "Erreur", "Veuillez sélectionner deux équipes!")
            return

        if equipe1_nom == equipe2_nom:
            self.show_error_popup(
                "Erreur", "Veuillez sélectionner deux équipes différentes!")
            return

        equipe1 = self.nba_system.rechercher_equipe(equipe1_nom)
        equipe2 = self.nba_system.rechercher_equipe(equipe2_nom)

        if not equipe1 or not equipe2:
            self.show_error_popup("Erreur", "Une des équipes n'existe pas!")
            return

        # Générer la comparaison
        comparaison = self.generer_comparaison_equipes(equipe1, equipe2)

        self.comparaison_text.config(state=tk.NORMAL)
        self.comparaison_text.delete(1.0, tk.END)
        self.comparaison_text.insert(tk.END, comparaison)
        self.comparaison_text.config(state=tk.DISABLED)

    def generer_comparaison_equipes(self, equipe1, equipe2):
        """Générer une comparaison détaillée entre deux équipes"""
        comparaison = "=" * 80 + "\n"
        comparaison += f"⚖️ COMPARAISON: {equipe1.nom} vs {equipe2.nom}\n"
        comparaison += "=" * 80 + "\n\n"

        # Bilans
        comparaison += "📊 BILANS:\n"
        comparaison += f"   {equipe1.nom:.<30} {equipe1.victoires}V - {equipe1.defaites}D ({equipe1.calculer_pourcentage_victoires():.1f}%)\n"
        comparaison += f"   {equipe2.nom:.<30} {equipe2.victoires}V - {equipe2.defaites}D ({equipe2.calculer_pourcentage_victoires():.1f}%)\n\n"

        # Effectifs
        comparaison += "👥 EFFECTIFS:\n"
        comparaison += f"   {equipe1.nom:.<30} {len(equipe1.joueurs)} joueurs\n"
        comparaison += f"   {equipe2.nom:.<30} {len(equipe2.joueurs)} joueurs\n\n"

        # Statistiques moyennes
        stats1 = equipe1.obtenir_statistiques_equipe()
        stats2 = equipe2.obtenir_statistiques_equipe()

        if stats1 and stats2:
            comparaison += "📈 STATISTIQUES MOYENNES:\n"
            comparaison += f"   Points par joueur:\n"
            comparaison += f"      {equipe1.nom:.<25} {stats1['points_moyens']:.1f} pts\n"
            comparaison += f"      {equipe2.nom:.<25} {stats2['points_moyens']:.1f} pts\n"

            comparaison += f"   Passes par joueur:\n"
            comparaison += f"      {equipe1.nom:.<25} {stats1['passes_moyennes']:.1f}\n"
            comparaison += f"      {equipe2.nom:.<25} {stats2['passes_moyennes']:.1f}\n"

            comparaison += f"   Rebonds par joueur:\n"
            comparaison += f"      {equipe1.nom:.<25} {stats1['rebonds_moyens']:.1f}\n"
            comparaison += f"      {equipe2.nom:.<25} {stats2['rebonds_moyens']:.1f}\n\n"

        # Confrontations directes
        confrontations = []
        for match in self.nba_system._matchs:
            if ((match.equipe_domicile == equipe1 and match.equipe_exterieur == equipe2) or
                    (match.equipe_domicile == equipe2 and match.equipe_exterieur == equipe1)):
                confrontations.append(match)

        if confrontations:
            comparaison += f"🏆 CONFRONTATIONS DIRECTES ({len(confrontations)} matchs):\n"
            victoires_e1 = 0
            victoires_e2 = 0

            for match in confrontations:
                gagnant = match.get_equipe_gagnante()
                if gagnant == equipe1:
                    victoires_e1 += 1
                elif gagnant == equipe2:
                    victoires_e2 += 1

                comparaison += f"   {match.date.strftime('%Y-%m-%d')}: "
                if match.equipe_domicile == equipe1:
                    comparaison += f"{equipe1.nom} {match.score_domicile} - {match.score_exterieur} {equipe2.nom}"
                else:
                    comparaison += f"{equipe2.nom} {match.score_domicile} - {match.score_exterieur} {equipe1.nom}"

                if gagnant:
                    comparaison += f" (Victoire {gagnant.nom})\n"
                else:
                    comparaison += " (Égalité)\n"

            comparaison += f"\n   Bilan H2H:\n"
            comparaison += f"      {equipe1.nom}: {victoires_e1} victoires\n"
            comparaison += f"      {equipe2.nom}: {victoires_e2} victoires\n"
        else:
            comparaison += "🏆 CONFRONTATIONS DIRECTES: Aucune\n"

        comparaison += "\n" + "=" * 80
        return comparaison

    def analyser_tendances(self):
        """Analyser les tendances des équipes"""
        analyse = "=" * 80 + "\n"
        analyse += "📈 ANALYSE DES TENDANCES\n"
        analyse += "=" * 80 + "\n\n"

        # Équipes avec le meilleur pourcentage
        classement = self.nba_system.obtenir_classement()
        if classement:
            analyse += "🏆 TOP 3 ÉQUIPES:\n"
            for i, equipe in enumerate(classement[:3], 1):
                analyse += f"   {i}. {equipe.nom} - {equipe.calculer_pourcentage_victoires():.1f}% ({equipe.victoires}V/{equipe.defaites}D)\n"
            analyse += "\n"

        # Analyse des matchs récents (5 derniers)
        matchs_recents = sorted(self.nba_system._matchs,
                                key=lambda m: m.date, reverse=True)[:5]
        if matchs_recents:
            analyse += "⚡ MATCHS RÉCENTS (5 derniers):\n"
            for match in matchs_recents:
                gagnant = match.get_equipe_gagnante()
                ecart = match.get_ecart_points()
                type_match = "serré" if ecart <= 5 else "large"

                analyse += f"   {match.date.strftime('%Y-%m-%d')}: {match.equipe_domicile.nom} {match.score_domicile} - {match.score_exterieur} {match.equipe_exterieur.nom}"
                if gagnant:
                    analyse += f" (Victoire {type_match} de {gagnant.nom})\n"
                else:
                    analyse += " (Égalité)\n"
            analyse += "\n"

        # Statistiques globales
        total_matchs = len(self.nba_system._matchs)
        if total_matchs > 0:
            matchs_serres = sum(
                1 for m in self.nba_system._matchs if m.est_match_serre())
            pourcentage_serres = (matchs_serres / total_matchs) * 100

            analyse += "📊 STATISTIQUES GLOBALES:\n"
            analyse += f"   • Total de matchs: {total_matchs}\n"
            analyse += f"   • Matchs serrés (≤5 pts): {matchs_serres} ({pourcentage_serres:.1f}%)\n"
            analyse += f"   • Compétitivité: {'Très élevée' if pourcentage_serres > 50 else 'Élevée' if pourcentage_serres > 30 else 'Modérée'}\n"

        self.analyse_text.config(state=tk.NORMAL)
        self.analyse_text.delete(1.0, tk.END)
        self.analyse_text.insert(tk.END, analyse)
        self.analyse_text.config(state=tk.DISABLED)

    def joueurs_en_forme(self):
        """Identifier les joueurs en forme"""
        analyse = "=" * 80 + "\n"
        analyse += "⭐ JOUEURS EN FORME\n"
        analyse += "=" * 80 + "\n\n"

        # Top scoreurs
        top_scoreurs = self.nba_system.obtenir_top_joueurs('points', 5)
        if top_scoreurs:
            analyse += "🏀 TOP SCOREURS:\n"
            for i, (joueur, moyennes) in enumerate(top_scoreurs, 1):
                equipe = joueur.equipe.nom if joueur.equipe else "Libre"
                analyse += f"   {i}. {joueur.nom} ({equipe}) - {moyennes['points']:.1f} pts/match\n"
            analyse += "\n"

        # Top passeurs
        top_passeurs = self.nba_system.obtenir_top_joueurs('passes', 5)
        if top_passeurs:
            analyse += "🎯 TOP PASSEURS:\n"
            for i, (joueur, moyennes) in enumerate(top_passeurs, 1):
                equipe = joueur.equipe.nom if joueur.equipe else "Libre"
                analyse += f"   {i}. {joueur.nom} ({equipe}) - {moyennes['passes']:.1f} passes/match\n"
            analyse += "\n"

        # Top rebondeurs
        top_rebondeurs = self.nba_system.obtenir_top_joueurs('rebonds', 5)
        if top_rebondeurs:
            analyse += "💪 TOP REBONDEURS:\n"
            for i, (joueur, moyennes) in enumerate(top_rebondeurs, 1):
                equipe = joueur.equipe.nom if joueur.equipe else "Libre"
                analyse += f"   {i}. {joueur.nom} ({equipe}) - {moyennes['rebonds']:.1f} rebonds/match\n"
            analyse += "\n"

        # Joueurs les plus efficaces
        top_efficaces = self.nba_system.obtenir_top_joueurs(
            'efficacite_moyenne', 5)
        if top_efficaces:
            analyse += "⚡ JOUEURS LES PLUS EFFICACES:\n"
            for i, (joueur, moyennes) in enumerate(top_efficaces, 1):
                equipe = joueur.equipe.nom if joueur.equipe else "Libre"
                analyse += f"   {i}. {joueur.nom} ({equipe}) - {moyennes['efficacite_moyenne']:.2f} d'efficacité\n"

        self.analyse_text.config(state=tk.NORMAL)
        self.analyse_text.delete(1.0, tk.END)
        self.analyse_text.insert(tk.END, analyse)
        self.analyse_text.config(state=tk.DISABLED)

    def equipes_en_difficulte(self):
        """Identifier les équipes en difficulté"""
        analyse = "=" * 80 + "\n"
        analyse += "📉 ÉQUIPES EN DIFFICULTÉ\n"
        analyse += "=" * 80 + "\n\n"

        # Équipes avec le plus faible pourcentage
        classement = self.nba_system.obtenir_classement()
        equipes_difficulte = [
            e for e in classement if e.calculer_pourcentage_victoires() < 40]

        if equipes_difficulte:
            analyse += "⚠️ ÉQUIPES SOUS 40% DE VICTOIRES:\n"
            for equipe in equipes_difficulte:
                pourcentage = equipe.calculer_pourcentage_victoires()
                analyse += f"   • {equipe.nom}: {pourcentage:.1f}% ({equipe.victoires}V/{equipe.defaites}D)\n"

                # Analyser les problèmes potentiels
                if len(equipe.joueurs) < 10:
                    analyse += f"     ⚠️ Effectif réduit: {len(equipe.joueurs)} joueurs\n"

                stats_equipe = equipe.obtenir_statistiques_equipe()
                if stats_equipe and stats_equipe['points_moyens'] < 15:
                    analyse += f"     ⚠️ Attaque faible: {stats_equipe['points_moyens']:.1f} pts/joueur\n"
            analyse += "\n"

        # Équipes sans victoire
        equipes_sans_victoire = [e for e in self.nba_system._equipes.values(
        ) if e.victoires == 0 and e.defaites > 0]
        if equipes_sans_victoire:
            analyse += "🚨 ÉQUIPES SANS VICTOIRE:\n"
            for equipe in equipes_sans_victoire:
                analyse += f"   • {equipe.nom}: 0 victoire - {equipe.defaites} défaites\n"
            analyse += "\n"

        # Recommandations
        analyse += "💡 RECOMMANDATIONS:\n"
        analyse += "   • Renforcer l'effectif des équipes sous-dimensionnées\n"
        analyse += "   • Analyser les statistiques individuelles des joueurs\n"
        analyse += "   • Considérer des transferts stratégiques\n"
        analyse += "   • Travailler sur l'efficacité offensive\n"

        if not equipes_difficulte and not equipes_sans_victoire:
            analyse += "✅ Aucune équipe en difficulté majeure détectée!\n"
            analyse += "Toutes les équipes maintiennent un niveau correct.\n"

        self.analyse_text.config(state=tk.NORMAL)
        self.analyse_text.delete(1.0, tk.END)
        self.analyse_text.insert(tk.END, analyse)
        self.analyse_text.config(state=tk.DISABLED)

    # =====================================
    # Méthodes utilitaires améliorées
    # =====================================

    def actualiser_comboboxes(self):
        """Actualiser toutes les comboboxes avec les données actuelles"""
        # Liste des équipes
        equipes_noms = list(self.nba_system._equipes.keys())

        # Mettre à jour les comboboxes d'équipes
        self.joueur_equipe_combo['values'] = equipes_noms
        self.transfer_equipe_combo['values'] = equipes_noms
        self.match_domicile_combo['values'] = equipes_noms
        self.match_exterieur_combo['values'] = equipes_noms
        self.compare_equipe1_combo['values'] = equipes_noms
        self.compare_equipe2_combo['values'] = equipes_noms

        # Liste des joueurs
        joueurs_noms = list(self.nba_system._joueurs_index.keys())

        # Mettre à jour les comboboxes de joueurs
        self.transfer_joueur_combo['values'] = joueurs_noms
        self.stats_joueur_combo['values'] = joueurs_noms

    def actualiser_tout(self):
        """Actualiser toutes les vues"""
        self.actualiser_equipes()
        self.actualiser_joueurs()
        self.actualiser_matchs()
        self.actualiser_statistiques()
        self.actualiser_comboboxes()
        self.show_success_popup(
            "Succès", "Toutes les données ont été actualisées!")

    def verifier_coherence(self):
        """Vérifier la cohérence du système et afficher les incohérences"""
        incoherences = self.nba_system.valider_coherence_systeme()

        if not incoherences:
            self.show_success_popup(
                "Vérification", "✅ Aucune incohérence détectée!\nLe système est cohérent.")
        else:
            # Créer une fenêtre popup pour afficher les incohérences
            self.create_incoherences_window(incoherences)

    def sauvegarder_donnees(self):
        """Sauvegarder les données du système"""
        try:
            donnees = {
                'equipes': [],
                'joueurs': [],
                'matchs': []
            }

            # Sauvegarder les équipes
            for equipe in self.nba_system._equipes.values():
                donnees['equipes'].append({
                    'nom': equipe.nom,
                    'ville': equipe.ville,
                    'victoires': equipe.victoires,
                    'defaites': equipe.defaites
                })

            # Sauvegarder les joueurs
            for joueur in self.nba_system._joueurs_index.values():
                joueur_data = {
                    'nom': joueur.nom,
                    'origine': joueur.origine,
                    'annee_debut': joueur.annee_debut,
                    'poste': joueur.poste.value,
                    'equipe': joueur.equipe.nom if joueur.equipe else None,
                    'statistiques': []
                }

                for stat in joueur._statistiques:
                    joueur_data['statistiques'].append({
                        'temps_jeu': stat.temps_jeu,
                        'points': stat.points,
                        'passes': stat.passes,
                        'rebonds': stat.rebonds,
                        'date': stat.date_match.isoformat()
                    })

                donnees['joueurs'].append(joueur_data)

            # Sauvegarder les matchs
            for match in self.nba_system._matchs:
                donnees['matchs'].append({
                    'equipe_domicile': match.equipe_domicile.nom,
                    'equipe_exterieur': match.equipe_exterieur.nom,
                    'score_domicile': match.score_domicile,
                    'score_exterieur': match.score_exterieur,
                    'date': match.date.isoformat()
                })

            # Sauvegarder dans un fichier
            filename = f"nba_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(donnees, f, indent=2, ensure_ascii=False)

            self.show_success_popup(
                "Sauvegarde", f"Données sauvegardées dans {filename}")

        except Exception as e:
            self.show_error_popup("Erreur de sauvegarde",
                                  f"Impossible de sauvegarder: {e}")

    def charger_donnees(self):
        """Charger des données depuis un fichier"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Charger des données NBA",
                filetypes=[("Fichiers JSON", "*.json")]
            )

            if not filename:
                return

            with open(filename, 'r', encoding='utf-8') as f:
                donnees = json.load(f)

            # Confirmer le chargement
            if messagebox.askyesno("Confirmation",
                                   "Cette action remplacera toutes les données actuelles.\n"
                                   "Voulez-vous continuer?"):

                # Réinitialiser le système
                self.nba_system = NBASystem()

                # Charger les équipes
                for equipe_data in donnees.get('equipes', []):
                    equipe = self.nba_system.ajouter_equipe(
                        equipe_data['nom'], equipe_data['ville'])
                    # Restaurer les bilans
                    equipe._victoires = equipe_data.get('victoires', 0)
                    equipe._defaites = equipe_data.get('defaites', 0)

                # Charger les joueurs
                for joueur_data in donnees.get('joueurs', []):
                    if joueur_data.get('equipe'):
                        self.nba_system.ajouter_joueur_a_equipe(
                            joueur_data['equipe'],
                            joueur_data['nom'],
                            joueur_data['origine'],
                            joueur_data['annee_debut'],
                            joueur_data['poste']
                        )

                        # Charger les statistiques
                        joueur = self.nba_system.rechercher_joueur(
                            joueur_data['nom'])
                        for stat_data in joueur_data.get('statistiques', []):
                            date_match = datetime.fromisoformat(
                                stat_data['date'])
                            joueur.ajouter_statistiques(
                                stat_data['temps_jeu'],
                                stat_data['points'],
                                stat_data['passes'],
                                stat_data['rebonds'],
                                date_match
                            )

                # Réinitialiser les bilans avant de charger les matchs
                for equipe in self.nba_system._equipes.values():
                    equipe._victoires = 0
                    equipe._defaites = 0

                # Charger les matchs
                for match_data in donnees.get('matchs', []):
                    date_match = datetime.fromisoformat(match_data['date'])
                    self.nba_system.ajouter_match(
                        match_data['equipe_domicile'],
                        match_data['equipe_exterieur'],
                        match_data['score_domicile'],
                        match_data['score_exterieur'],
                        date_match.strftime('%Y-%m-%d')
                    )

                # Actualiser toutes les vues
                self.actualiser_tout()
                self.show_success_popup(
                    "Chargement", f"Données chargées depuis {filename}")

        except Exception as e:
            self.show_error_popup("Erreur de chargement",
                                  f"Impossible de charger les données: {e}")

    def charger_donnees_exemple(self):
        """Charger des données d'exemple améliorées"""
        try:
            # Création d'équipes
            equipes_data = [
                ("Chicago Bulls", "Chicago"),
                ("Los Angeles Lakers", "Los Angeles"),
                ("Boston Celtics", "Boston"),
                ("Golden State Warriors", "San Francisco"),
                ("Miami Heat", "Miami"),
                ("Brooklyn Nets", "Brooklyn")
            ]

            for nom, ville in equipes_data:
                self.nba_system.ajouter_equipe(nom, ville)

            # Ajout de joueurs avec plus de variété
            joueurs_data = [
                ("Chicago Bulls", "Michael Jordan", "USA", 1984, "Shooting Guard"),
                ("Chicago Bulls", "Scottie Pippen", "USA", 1987, "Small Forward"),
                ("Chicago Bulls", "Dennis Rodman", "USA", 1986, "Power Forward"),
                ("Los Angeles Lakers", "LeBron James",
                 "USA", 2003, "Small Forward"),
                ("Los Angeles Lakers", "Anthony Davis",
                 "USA", 2012, "Power Forward"),
                ("Los Angeles Lakers", "Russell Westbrook",
                 "USA", 2008, "Point Guard"),
                ("Boston Celtics", "Jayson Tatum", "USA", 2017, "Small Forward"),
                ("Boston Celtics", "Jaylen Brown", "USA", 2016, "Shooting Guard"),
                ("Golden State Warriors", "Stephen Curry",
                 "USA", 2009, "Point Guard"),
                ("Golden State Warriors", "Klay Thompson",
                 "USA", 2011, "Shooting Guard"),
                ("Miami Heat", "Jimmy Butler", "USA", 2011, "Small Forward"),
                ("Brooklyn Nets", "Kevin Durant", "USA", 2007, "Small Forward")
            ]

            for equipe, nom, origine, annee, poste in joueurs_data:
                self.nba_system.ajouter_joueur_a_equipe(
                    equipe, nom, origine, annee, poste)

            # Ajout de statistiques variées
            stats_joueurs = {
                "Michael Jordan": [(38.2, 30.1, 6.2, 5.2), (40.5, 33.4, 6.9, 5.9), (42.0, 35.0, 8.0, 6.5)],
                "LeBron James": [(36.9, 27.1, 7.4, 7.4), (38.0, 29.5, 8.2, 7.8), (35.5, 25.8, 6.8, 8.1)],
                "Stephen Curry": [(34.7, 29.5, 6.1, 5.2), (36.0, 31.2, 5.8, 4.9), (33.5, 27.8, 5.5, 4.2)],
                "Jayson Tatum": [(35.5, 26.8, 4.2, 8.0), (37.2, 28.1, 4.8, 7.5), (36.0, 24.5, 4.0, 7.8)],
                "Anthony Davis": [(34.0, 23.5, 2.3, 9.9), (35.2, 25.8, 2.8, 10.2), (32.5, 21.2, 2.1, 8.8)],
                "Jimmy Butler": [(33.8, 21.4, 5.9, 6.9), (35.0, 22.8, 6.2, 7.1), (34.2, 20.9, 5.5, 6.5)]
            }

            for nom_joueur, stats_list in stats_joueurs.items():
                joueur = self.nba_system.rechercher_joueur(nom_joueur)
                if joueur:
                    for temps, points, passes, rebonds in stats_list:
                        joueur.ajouter_statistiques(
                            temps, points, passes, rebonds)

            # Ajout de matchs avec plus de variété
            matchs_data = [
                ("Chicago Bulls", "Los Angeles Lakers", 108, 102, "2024-01-15"),
                ("Boston Celtics", "Chicago Bulls", 95, 110, "2024-01-20"),
                ("Los Angeles Lakers", "Boston Celtics", 115, 112, "2024-01-25"),
                ("Golden State Warriors", "Chicago Bulls", 120, 105, "2024-02-01"),
                ("Los Angeles Lakers", "Golden State Warriors", 118, 123, "2024-02-05"),
                ("Boston Celtics", "Golden State Warriors", 107, 104, "2024-02-10"),
                ("Miami Heat", "Brooklyn Nets", 98, 95, "2024-02-15"),
                ("Chicago Bulls", "Miami Heat", 102, 89, "2024-02-20"),
                ("Golden State Warriors", "Miami Heat", 125, 118, "2024-02-25"),
                ("Brooklyn Nets", "Los Angeles Lakers", 109, 116, "2024-03-01")
            ]

            for dom, ext, score_dom, score_ext, date in matchs_data:
                self.nba_system.ajouter_match(
                    dom, ext, score_dom, score_ext, date)

            # Actualiser toutes les vues
            self.actualiser_equipes()
            self.actualiser_joueurs()
            self.actualiser_matchs()
            self.actualiser_statistiques()
            self.actualiser_comboboxes()

        except Exception as e:
            print(f"Erreur lors du chargement des données d'exemple: {e}")

    # =====================================
    # Méthodes pour les popups améliorées
    # =====================================

    def show_success_popup(self, title, message):
        """Afficher un popup de succès"""
        messagebox.showinfo(title, message)

    def show_error_popup(self, title, message):
        """Afficher un popup d'erreur"""
        messagebox.showerror(title, message)

    def show_warning_popup(self, title, message):
        """Afficher un popup d'avertissement"""
        messagebox.showwarning(title, message)

    def show_info_popup(self, title, message):
        """Afficher un popup d'information"""
        messagebox.showinfo(title, message)

    def create_incoherences_window(self, incoherences):
        """Créer une fenêtre pour afficher les incohérences"""
        popup = tk.Toplevel(self.root)
        popup.title("⚠️ Incohérences détectées")
        popup.geometry("600x400")
        popup.configure(bg='#f8f9fa')

        # En-tête
        header = tk.Label(popup, text="⚠️ INCOHÉRENCES DÉTECTÉES",
                          font=('Arial', 16, 'bold'),
                          bg='#f8f9fa', fg='#e74c3c')
        header.pack(pady=10)

        # Frame pour la liste
        list_frame = tk.Frame(popup, bg='#f8f9fa')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Text widget avec scrollbar
        text_widget = tk.Text(list_frame, wrap=tk.WORD,
                              font=('Courier', 10),
                              bg='white', relief='solid', bd=1)
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Contenu
        contenu = f"Nombre d'incohérences trouvées: {len(incoherences)}\n\n"
        for i, incoherence in enumerate(incoherences, 1):
            contenu += f"{i}. {incoherence}\n"

        text_widget.insert(tk.END, contenu)
        text_widget.config(state=tk.DISABLED)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Boutons
        button_frame = tk.Frame(popup, bg='#f8f9fa')
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Fermer",
                   command=popup.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Corriger automatiquement",
                   command=lambda: self.corriger_incoherences(incoherences, popup)).pack(side=tk.LEFT, padx=5)

    def corriger_incoherences(self, incoherences, popup):
        """Tenter de corriger automatiquement certaines incohérences"""
        corrections = 0

        for incoherence in incoherences:
            if "n'appartient à aucune équipe" in incoherence:
                # Essayer d'assigner le joueur à une équipe avec de la place
                nom_joueur = incoherence.split()[1]
                joueur = self.nba_system.rechercher_joueur(nom_joueur)

                if joueur:
                    for equipe in self.nba_system._equipes.values():
                        if len(equipe.joueurs) < equipe.MAX_JOUEURS:
                            try:
                                equipe.ajouter_joueur(joueur)
                                corrections += 1
                                break
                            except:
                                continue

        popup.destroy()
        if corrections > 0:
            self.show_success_popup(
                "Corrections", f"{corrections} incohérence(s) corrigée(s)")
            self.actualiser_tout()
        else:
            self.show_warning_popup(
                "Corrections", "Aucune correction automatique possible")

    def create_equipe_details_window(self, equipe):
        """Créer une fenêtre détaillée pour une équipe"""
        popup = tk.Toplevel(self.root)
        popup.title(f"🏀 Détails - {equipe.nom}")
        popup.geometry("700x600")
        popup.configure(bg='#f8f9fa')

        # En-tête
        header_frame = tk.Frame(popup, bg='#3498db', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text=f"🏀 {equipe.nom}",
                 font=('Arial', 20, 'bold'),
                 bg='#3498db', fg='white').pack(expand=True)
        tk.Label(header_frame, text=f"📍 {equipe.ville}",
                 font=('Arial', 12),
                 bg='#3498db', fg='#ecf0f1').pack()

        # Contenu avec onglets
        notebook = ttk.Notebook(popup)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Onglet informations générales
        info_frame = tk.Frame(notebook, bg='white')
        notebook.add(info_frame, text="📊 Informations")

        info_text = tk.Text(info_frame, wrap=tk.WORD, font=('Courier', 11),
                            bg='#f8f9fa', relief='solid', bd=1)
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Contenu des informations
        details = f"=== {equipe.nom} ({equipe.ville}) ===\n\n"
        details += f"📈 BILAN GÉNÉRAL:\n"
        details += f"   • Victoires: {equipe.victoires}\n"
        details += f"   • Défaites: {equipe.defaites}\n"
        details += f"   • Pourcentage: {equipe.calculer_pourcentage_victoires():.1f}%\n"
        details += f"   • Total matchs: {equipe.victoires + equipe.defaites}\n\n"

        details += f"👥 EFFECTIF:\n"
        details += f"   • Joueurs: {len(equipe.joueurs)}/{equipe.MAX_JOUEURS}\n"
        details += f"   • Places disponibles: {equipe.MAX_JOUEURS - len(equipe.joueurs)}\n\n"

        if equipe.joueurs:
            details += f"🏀 LISTE DES JOUEURS:\n"
            for joueur in sorted(equipe.joueurs, key=lambda j: j.nom):
                moyennes = joueur.calculer_moyennes()
                if moyennes:
                    details += f"   • {joueur.nom} ({joueur.poste.value}) - {moyennes['points']:.1f} pts/match\n"
                else:
                    details += f"   • {joueur.nom} ({joueur.poste.value}) - Pas de statistiques\n"

            stats_equipe = equipe.obtenir_statistiques_equipe()
            if stats_equipe:
                details += f"\n📊 STATISTIQUES MOYENNES ÉQUIPE:\n"
                details += f"   • Joueurs actifs: {stats_equipe['joueurs_actifs']}\n"
                details += f"   • Points moyens par joueur: {stats_equipe['points_moyens']:.1f}\n"
                details += f"   • Passes moyennes par joueur: {stats_equipe['passes_moyennes']:.1f}\n"
                details += f"   • Rebonds moyens par joueur: {stats_equipe['rebonds_moyens']:.1f}\n"
        else:
            details += "👥 EFFECTIF: Aucun joueur dans l'équipe\n"

        info_text.insert(tk.END, details)
        info_text.config(state=tk.DISABLED)

        # Onglet historique des matchs
        matchs_frame = tk.Frame(notebook, bg='white')
        notebook.add(matchs_frame, text="⚡ Historique")

        matchs_equipe = self.nba_system.obtenir_matchs_equipe(equipe.nom)

        if matchs_equipe:
            # Treeview pour les matchs
            columns = ('Date', 'Adversaire', 'Lieu', 'Score', 'Résultat')
            matchs_tree = ttk.Treeview(
                matchs_frame, columns=columns, show='headings', height=15)

            for col in columns:
                matchs_tree.heading(col, text=col)
                matchs_tree.column(col, width=120)

            for match in sorted(matchs_equipe, key=lambda m: m.date, reverse=True):
                if match.equipe_domicile == equipe:
                    adversaire = match.equipe_exterieur.nom
                    lieu = "Domicile"
                    score = f"{match.score_domicile} - {match.score_exterieur}"
                else:
                    adversaire = match.equipe_domicile.nom
                    lieu = "Extérieur"
                    score = f"{match.score_exterieur} - {match.score_domicile}"

                gagnant = match.get_equipe_gagnante()
                if gagnant == equipe:
                    resultat = "Victoire"
                    tag = "victoire"
                elif gagnant is None:
                    resultat = "Égalité"
                    tag = "egalite"
                else:
                    resultat = "Défaite"
                    tag = "defaite"

                matchs_tree.insert('', 'end', values=(
                    match.date.strftime('%Y-%m-%d'),
                    adversaire,
                    lieu,
                    score,
                    resultat
                ), tags=(tag,))

            # Configuration des tags
            matchs_tree.tag_configure("victoire", background="#d4edda")
            matchs_tree.tag_configure("defaite", background="#f8d7da")
            matchs_tree.tag_configure("egalite", background="#fff3cd")

            matchs_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        else:
            tk.Label(matchs_frame, text="Aucun match disputé",
                     font=('Arial', 14), bg='white').pack(expand=True)

    def create_equipe_stats_window(self, equipe):
        """Créer une fenêtre de statistiques avancées pour une équipe"""
        popup = tk.Toplevel(self.root)
        popup.title(f"📊 Statistiques - {equipe.nom}")
        popup.geometry("600x500")
        popup.configure(bg='#f8f9fa')

        # Contenu
        text_widget = tk.Text(popup, wrap=tk.WORD, font=('Courier', 10),
                              bg='white', relief='solid', bd=1)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Générer les statistiques avancées
        stats = f"📊 STATISTIQUES AVANCÉES - {equipe.nom}\n"
        stats += "=" * 50 + "\n\n"

        # Analyse de l'effectif par poste
        postes_count = {}
        for joueur in equipe.joueurs:
            poste = joueur.poste.value
            postes_count[poste] = postes_count.get(poste, 0) + 1

        if postes_count:
            stats += "👥 RÉPARTITION PAR POSTE:\n"
            for poste, count in postes_count.items():
                stats += f"   • {poste}: {count} joueur(s)\n"
            stats += "\n"

        # Analyse des performances
        matchs_equipe = self.nba_system.obtenir_matchs_equipe(equipe.nom)
        if matchs_equipe:
            victoires_dom = sum(
                1 for m in matchs_equipe if m.equipe_domicile == equipe and m.get_equipe_gagnante() == equipe)
            victoires_ext = sum(
                1 for m in matchs_equipe if m.equipe_exterieur == equipe and m.get_equipe_gagnante() == equipe)
            matchs_dom = sum(
                1 for m in matchs_equipe if m.equipe_domicile == equipe)
            matchs_ext = sum(
                1 for m in matchs_equipe if m.equipe_exterieur == equipe)

            stats += "🏠 PERFORMANCES DOMICILE/EXTÉRIEUR:\n"
            stats += f"   • Domicile: {victoires_dom}/{matchs_dom} ({(victoires_dom / matchs_dom * 100) if matchs_dom > 0 else 0:.1f}%)\n"
            stats += f"   • Extérieur: {victoires_ext}/{matchs_ext} ({(victoires_ext / matchs_ext * 100) if matchs_ext > 0 else 0:.1f}%)\n\n"

            # Analyse des scores
            scores_pour = []
            scores_contre = []

            for match in matchs_equipe:
                if match.equipe_domicile == equipe:
                    scores_pour.append(match.score_domicile)
                    scores_contre.append(match.score_exterieur)
                else:
                    scores_pour.append(match.score_exterieur)
                    scores_contre.append(match.score_domicile)

            if scores_pour:
                stats += "📈 ANALYSE OFFENSIVE/DÉFENSIVE:\n"
                stats += f"   • Points marqués (moyenne): {sum(scores_pour) / len(scores_pour):.1f}\n"
                stats += f"   • Points encaissés (moyenne): {sum(scores_contre) / len(scores_contre):.1f}\n"
                stats += f"   • Différentiel: {(sum(scores_pour) - sum(scores_contre)) / len(scores_pour):.1f}\n"
                stats += f"   • Meilleur score: {max(scores_pour)}\n"
                stats += f"   • Score le plus faible: {min(scores_pour)}\n\n"

        # Top joueurs de l'équipe
        joueurs_avec_stats = [(j, j.calculer_moyennes())
                              for j in equipe.joueurs if j.calculer_moyennes()]
        if joueurs_avec_stats:
            stats += "⭐ TOP JOUEURS DE L'ÉQUIPE:\n"

            # Top scoreur
            top_scoreur = max(joueurs_avec_stats, key=lambda x: x[1]['points'])
            stats += f"   • Meilleur scoreur: {top_scoreur[0].nom} ({top_scoreur[1]['points']:.1f} pts)\n"

            # Top passeur
            top_passeur = max(joueurs_avec_stats, key=lambda x: x[1]['passes'])
            stats += f"   • Meilleur passeur: {top_passeur[0].nom} ({top_passeur[1]['passes']:.1f} passes)\n"

            # Top rebondeur
            top_rebondeur = max(joueurs_avec_stats,
                                key=lambda x: x[1]['rebonds'])
            stats += f"   • Meilleur rebondeur: {top_rebondeur[0].nom} ({top_rebondeur[1]['rebonds']:.1f} rebonds)\n"

        text_widget.insert(tk.END, stats)
        text_widget.config(state=tk.DISABLED)

    def create_joueur_stats_window(self, joueur):
        """Créer une fenêtre de statistiques détaillées pour un joueur"""
        popup = tk.Toplevel(self.root)
        popup.title(f"👤 Statistiques - {joueur.nom}")
        popup.geometry("600x500")
        popup.configure(bg='#f8f9fa')

        # En-tête avec photo stylisée
        header_frame = tk.Frame(popup, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text=f"👤 {joueur.nom}",
                 font=('Arial', 18, 'bold'),
                 bg='#2c3e50', fg='white').pack(expand=True)
        tk.Label(header_frame, text=f"{joueur.poste.value} • {joueur.equipe.nom if joueur.equipe else 'Libre'}",
                 font=('Arial', 11),
                 bg='#2c3e50', fg='#bdc3c7').pack()

        # Notebook pour les différentes vues
        notebook = ttk.Notebook(popup)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Onglet statistiques générales
        stats_frame = tk.Frame(notebook, bg='white')
        notebook.add(stats_frame, text="📊 Statistiques")

        stats_text = tk.Text(stats_frame, wrap=tk.WORD, font=('Courier', 10),
                             bg='#f8f9fa', relief='solid', bd=1)
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Contenu des statistiques
        details = f"📊 FICHE JOUEUR - {joueur.nom}\n"
        details += "=" * 40 + "\n\n"

        details += f"ℹ️ INFORMATIONS GÉNÉRALES:\n"
        details += f"   • Nom: {joueur.nom}\n"
        details += f"   • Poste: {joueur.poste.value}\n"
        details += f"   • Origine: {joueur.origine}\n"
        details += f"   • Année de début: {joueur.annee_debut}\n"
        details += f"   • Équipe actuelle: {joueur.equipe.nom if joueur.equipe else 'Aucune'}\n"
        details += f"   • Expérience: {datetime.now().year - joueur.annee_debut} ans\n\n"

        moyennes = joueur.calculer_moyennes()
        if moyennes:
            details += f"📈 MOYENNES SUR {moyennes['matchs_joues']} MATCH(S):\n"
            details += f"   • Temps de jeu: {moyennes['temps_jeu']:.1f} min\n"
            details += f"   • Points: {moyennes['points']:.1f} pts\n"
            details += f"   • Passes décisives: {moyennes['passes']:.1f}\n"
            details += f"   • Rebonds: {moyennes['rebonds']:.1f}\n"
            details += f"   • Efficacité: {moyennes['efficacite_moyenne']:.2f}\n\n"

            meilleures = joueur.obtenir_meilleures_stats()
            if meilleures:
                details += f"🏆 RECORDS PERSONNELS:\n"
                details += f"   • Meilleur score: {meilleures['meilleur_score']} points\n"
                details += f"   • Meilleures passes: {meilleures['meilleur_passes']}\n"
                details += f"   • Meilleurs rebonds: {meilleures['meilleur_rebonds']}\n\n"

            # Évaluation du joueur
            points_moy = moyennes['points']
            if points_moy >= 25:
                niveau = "⭐⭐⭐ SUPERSTAR"
            elif points_moy >= 20:
                niveau = "⭐⭐ ALL-STAR"
            elif points_moy >= 15:
                niveau = "⭐ TITULAIRE"
            elif points_moy >= 10:
                niveau = "ROTATION"
            else:
                niveau = "REMPLAÇANT"

            details += f"🎯 ÉVALUATION: {niveau}\n"
        else:
            details += "📊 STATISTIQUES: Aucune donnée disponible\n"

        stats_text.insert(tk.END, details)
        stats_text.config(state=tk.DISABLED)

        # Onglet historique des performances
        if moyennes:
            histo_frame = tk.Frame(notebook, bg='white')
            notebook.add(histo_frame, text="📈 Historique")

            # Treeview pour l'historique
            columns = ('Date', 'Temps', 'Points',
                       'Passes', 'Rebonds', 'Efficacité')
            histo_tree = ttk.Treeview(
                histo_frame, columns=columns, show='headings', height=12)

            for col in columns:
                histo_tree.heading(col, text=col)
                histo_tree.column(col, width=80)

            for stat in sorted(joueur._statistiques, key=lambda s: s.date_match, reverse=True):
                efficacite = stat.calculer_efficacite()

                # Déterminer le tag selon la performance
                if stat.points >= 25:
                    tag = "excellent"
                elif stat.points >= 15:
                    tag = "bon"
                else:
                    tag = "normal"

                histo_tree.insert('', 'end', values=(
                    stat.date_match.strftime('%Y-%m-%d'),
                    f"{stat.temps_jeu:.0f}",
                    stat.points,
                    stat.passes,
                    stat.rebonds,
                    f"{efficacite:.2f}"
                ), tags=(tag,))

            # Configuration des tags
            histo_tree.tag_configure("excellent", background="#d4edda")
            histo_tree.tag_configure("bon", background="#fff3cd")
            histo_tree.tag_configure("normal", background="#f2f2f2")

            histo_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_match_analysis_window(self, match):
        """Créer une fenêtre d'analyse détaillée pour un match"""
        popup = tk.Toplevel(self.root)
        popup.title(f"⚡ Analyse du match - {match.date.strftime('%Y-%m-%d')}")
        popup.geometry("700x500")
        popup.configure(bg='#f8f9fa')

        # En-tête avec le score
        header_frame = tk.Frame(popup, bg='#34495e', height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Score principal
        score_frame = tk.Frame(header_frame, bg='#34495e')
        score_frame.pack(expand=True)

        tk.Label(score_frame, text=match.equipe_domicile.nom,
                 font=('Arial', 14, 'bold'),
                 bg='#34495e', fg='white').pack(side=tk.LEFT, padx=20)

        tk.Label(score_frame, text=f"{match.score_domicile} - {match.score_exterieur}",
                 font=('Arial', 20, 'bold'),
                 bg='#34495e', fg='#f39c12').pack(side=tk.LEFT, padx=20)

        tk.Label(score_frame, text=match.equipe_exterieur.nom,
                 font=('Arial', 14, 'bold'),
                 bg='#34495e', fg='white').pack(side=tk.LEFT, padx=20)

        # Date
        tk.Label(header_frame, text=match.date.strftime('%Y-%m-%d'),
                 font=('Arial', 12),
                 bg='#34495e', fg='#bdc3c7').pack()

        # Contenu de l'analyse
        text_widget = tk.Text(popup, wrap=tk.WORD, font=('Courier', 10),
                              bg='white', relief='solid', bd=1)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Générer l'analyse
        analyse = f"⚡ ANALYSE DÉTAILLÉE DU MATCH\n"
        analyse += "=" * 50 + "\n\n"

        analyse += f"📅 Date: {match.date.strftime('%d/%m/%Y')}\n"
        analyse += f"🏠 Domicile: {match.equipe_domicile.nom} ({match.equipe_domicile.ville})\n"
        analyse += f"✈️ Extérieur: {match.equipe_exterieur.nom} ({match.equipe_exterieur.ville})\n"
        analyse += f"📊 Score final: {match.score_domicile} - {match.score_exterieur}\n\n"

        # Résultat
        gagnant = match.get_equipe_gagnante()
        ecart = match.get_ecart_points()

        if gagnant:
            analyse += f"🏆 VAINQUEUR: {gagnant.nom}\n"
            analyse += f"📈 Écart: {ecart} points\n"

            if ecart <= 3:
                analyse += f"🔥 Type de match: TRÈS SERRÉ (thriller!)\n"
            elif ecart <= 7:
                analyse += f"⚡ Type de match: SERRÉ\n"
            elif ecart <= 15:
                analyse += f"📊 Type de match: ÉQUILIBRÉ\n"
            else:
                analyse += f"💪 Type de match: DOMINATION\n"
        else:
            analyse += f"🤝 RÉSULTAT: ÉGALITÉ PARFAITE!\n"

        analyse += "\n"

        # Impact sur les bilans
        analyse += f"📊 IMPACT SUR LES BILANS:\n\n"

        # Bilan équipe domicile
        analyse += f"🏠 {match.equipe_domicile.nom}:\n"
        analyse += f"   • Bilan actuel: {match.equipe_domicile.victoires}V - {match.equipe_domicile.defaites}D\n"
        analyse += f"   • Pourcentage: {match.equipe_domicile.calculer_pourcentage_victoires():.1f}%\n"

        # Bilan équipe extérieur
        analyse += f"✈️ {match.equipe_exterieur.nom}:\n"
        analyse += f"   • Bilan actuel: {match.equipe_exterieur.victoires}V - {match.equipe_exterieur.defaites}D\n"
        analyse += f"   • Pourcentage: {match.equipe_exterieur.calculer_pourcentage_victoires():.1f}%\n\n"

        # Analyse tactique basique
        analyse += f"🎯 ANALYSE TACTIQUE:\n\n"

        if match.score_domicile > 120 or match.score_exterieur > 120:
            analyse += f"🔥 Match à haute intensité offensive (score élevé)\n"
        elif match.score_domicile < 90 and match.score_exterieur < 90:
            analyse += f"🛡️ Match défensif avec des scores bas\n"
        else:
            analyse += f"⚖️ Match équilibré entre attaque et défense\n"

        # Avantage du terrain
        if match.equipe_domicile == gagnant:
            analyse += f"🏠 L'avantage du terrain a été déterminant\n"
        elif match.equipe_exterieur == gagnant:
            analyse += f"✈️ Victoire à l'extérieur - belle performance!\n"

        # Historique des confrontations
        confrontations = [m for m in self.nba_system._matchs
                          if ((
                              m.equipe_domicile == match.equipe_domicile and m.equipe_exterieur == match.equipe_exterieur) or
                              (
                              m.equipe_domicile == match.equipe_exterieur and m.equipe_exterieur == match.equipe_domicile))]

        if len(confrontations) > 1:
            analyse += f"\n📚 HISTORIQUE DES CONFRONTATIONS ({len(confrontations)} matchs):\n"
            victoires_dom = sum(
                1 for m in confrontations if m.get_equipe_gagnante() == match.equipe_domicile)
            victoires_ext = sum(
                1 for m in confrontations if m.get_equipe_gagnante() == match.equipe_exterieur)

            analyse += f"   • {match.equipe_domicile.nom}: {victoires_dom} victoire(s)\n"
            analyse += f"   • {match.equipe_exterieur.nom}: {victoires_ext} victoire(s)\n"

        text_widget.insert(tk.END, analyse)
        text_widget.config(state=tk.DISABLED)
