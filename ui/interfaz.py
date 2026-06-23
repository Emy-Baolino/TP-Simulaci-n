import tkinter as tk
from tkinter import ttk, messagebox

from core.motor_eventos import Simulador


# ----------------------------------------------------------------------
# Paleta "Palacio Ferreyra": inspirada en un museo de arte clásico —
# crema/marfil de fondo, borgoña como acento principal, dorado apagado
# como detalle, y un gris carbón para el texto.
# ----------------------------------------------------------------------
COLOR_FONDO = "#F5F0E6"        # marfil cálido
COLOR_PANEL = "#FFFFFF"
COLOR_BORGOÑA = "#7A1F2B"      # acento principal
COLOR_BORGOÑA_OSCURO = "#5C1620"
COLOR_DORADO = "#B08D57"       # detalle / hover
COLOR_TEXTO = "#2B2420"
COLOR_TEXTO_SUAVE = "#6B5F55"
COLOR_BORDE = "#D9CFC0"
FUENTE_TITULO = ("Georgia", 16, "bold")
FUENTE_SUBTITULO = ("Georgia", 11, "bold")
FUENTE_TEXTO = ("Segoe UI", 9)
FUENTE_MONO = ("Consolas", 9)


class InterfazApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador — Palacio Ferreyra | TP5 Simulación")
        self.root.configure(bg=COLOR_FONDO)
        self.root.geometry("1280x800")
        self.root.minsize(1024, 650)

        self.simulador_actual = None

        self._configurar_estilos()
        self._crear_variables()
        self._crear_layout()

    # ------------------------------------------------------------------
    # Estilos ttk
    # ------------------------------------------------------------------
    def _configurar_estilos(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=COLOR_FONDO)
        style.configure("Panel.TFrame", background=COLOR_PANEL, relief="flat")
        style.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO, font=FUENTE_TEXTO)
        style.configure("Panel.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXTO, font=FUENTE_TEXTO)
        style.configure("Titulo.TLabel", background=COLOR_FONDO, foreground=COLOR_BORGOÑA, font=FUENTE_TITULO)
        style.configure("Subtitulo.TLabel", background=COLOR_PANEL, foreground=COLOR_BORGOÑA_OSCURO, font=FUENTE_SUBTITULO)
        style.configure("Metrica.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXTO, font=("Segoe UI", 10))
        style.configure("MetricaValor.TLabel", background=COLOR_PANEL, foreground=COLOR_BORGOÑA, font=("Segoe UI", 12, "bold"))

        style.configure("TNotebook", background=COLOR_FONDO, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", COLOR_BORGOÑA)],
                  foreground=[("selected", "white")])

        style.configure("Accion.TButton", background=COLOR_BORGOÑA, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=10, borderwidth=0)
        style.map("Accion.TButton", background=[("active", COLOR_BORGOÑA_OSCURO)])

        style.configure("Treeview", background="white", fieldbackground="white",
                        foreground=COLOR_TEXTO, rowheight=24, font=FUENTE_MONO, borderwidth=0)
        style.configure("Treeview.Heading", background=COLOR_DORADO, foreground="white",
                        font=("Segoe UI", 9, "bold"), padding=6)
        style.map("Treeview.Heading", background=[("active", COLOR_BORGOÑA)])
        style.map("Treeview", background=[("selected", COLOR_BORGOÑA)], foreground=[("selected", "white")])

        style.configure("TLabelframe", background=COLOR_PANEL, foreground=COLOR_BORGOÑA_OSCURO, font=FUENTE_SUBTITULO)
        style.configure("TLabelframe.Label", background=COLOR_PANEL, foreground=COLOR_BORGOÑA_OSCURO, font=FUENTE_SUBTITULO)

    # ------------------------------------------------------------------
    # Variables de parámetros (todos modificables por el usuario)
    # ------------------------------------------------------------------
    def _crear_variables(self):
        self.media_a = tk.DoubleVar(value=90)
        self.desv_a = tk.DoubleVar(value=30)
        self.media_b = tk.DoubleVar(value=120)
        self.desv_b = tk.DoubleVar(value=40)
        self.media_c = tk.DoubleVar(value=60)
        self.desv_c = tk.DoubleVar(value=20)
        self.cerveza_min = tk.DoubleVar(value=50)
        self.cerveza_max = tk.DoubleVar(value=90)
        self.prob_folletos = tk.DoubleVar(value=60)
        self.prob_fotografia = tk.DoubleVar(value=40)
        self.prob_cerveza = tk.DoubleVar(value=50)

        self.param_j = tk.StringVar(value="0")
        self.param_i = tk.StringVar(value="80")
        self.param_dias = tk.IntVar(value=1)
        self.param_iter_max = tk.IntVar(value=100000)

        self.param_x = tk.DoubleVar(value=0.0)
        self.param_h = tk.DoubleVar(value=0.05)
        self.dist_salas = tk.StringVar(value="Normal")

        # Nuevas variables faltantes del enunciado
        self.folletos_media = tk.DoubleVar(value=10)
        self.folletos_desv = tk.DoubleVar(value=5)
        self.edad_media = tk.DoubleVar(value=30)

        self.salas_pint_m1 = tk.DoubleVar(value=300); self.salas_pint_d1 = tk.DoubleVar(value=60)
        self.salas_pint_m2 = tk.DoubleVar(value=220); self.salas_pint_d2 = tk.DoubleVar(value=60)
        self.salas_pint_m3 = tk.DoubleVar(value=310); self.salas_pint_d3 = tk.DoubleVar(value=60)
        self.salas_pint_m4 = tk.DoubleVar(value=350); self.salas_pint_d4 = tk.DoubleVar(value=60)

        self.salas_foto_m1 = tk.DoubleVar(value=190); self.salas_foto_d1 = tk.DoubleVar(value=60)
        self.salas_foto_m2 = tk.DoubleVar(value=200); self.salas_foto_d2 = tk.DoubleVar(value=60)
        self.salas_foto_m3 = tk.DoubleVar(value=250); self.salas_foto_d3 = tk.DoubleVar(value=60)
        self.salas_foto_m4 = tk.DoubleVar(value=180); self.salas_foto_d4 = tk.DoubleVar(value=60)

    # ------------------------------------------------------------------
    # Layout general: header + notebook con pestañas
    # ------------------------------------------------------------------
    def _crear_layout(self):
        self.main_canvas = tk.Canvas(self.root, bg=COLOR_FONDO, highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.main_frame = ttk.Frame(self.main_canvas, style="TFrame")
        
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        self.main_scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)
        
        self.main_window_id = self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        def _configure_main_frame(event):
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
            
        def _configure_main_canvas(event):
            if self.main_frame.winfo_reqwidth() < event.width:
                self.main_canvas.itemconfigure(self.main_window_id, width=event.width)
            else:
                self.main_canvas.itemconfigure(self.main_window_id, width=self.main_frame.winfo_reqwidth())
            
            if self.main_frame.winfo_reqheight() < event.height:
                self.main_canvas.itemconfigure(self.main_window_id, height=event.height)
            else:
                self.main_canvas.itemconfigure(self.main_window_id, height=self.main_frame.winfo_reqheight())

        self.main_frame.bind("<Configure>", _configure_main_frame)
        self.main_canvas.bind("<Configure>", _configure_main_canvas)
        
        def _on_mousewheel(event):
            try:
                w_class = event.widget.winfo_class()
                if w_class not in ('Treeview', 'Listbox', 'Scrollbar', 'TCombobox'):
                    self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception:
                pass

        self.root.bind_all("<MouseWheel>", _on_mousewheel)

        header = tk.Frame(self.main_frame, bg=COLOR_BORGOÑA, height=64)
        header.pack(fill="x", side="top")
        tk.Label(header, text="🏛  PALACIO FERREYRA", bg=COLOR_BORGOÑA, fg="white",
                 font=("Georgia", 18, "bold")).pack(side="left", padx=20, pady=10)
        tk.Label(header, text="Simulador de eventos discretos — TP5 Simulación 2026",
                 bg=COLOR_BORGOÑA, fg="#EBD9D9", font=("Segoe UI", 10, "italic")).pack(side="left", pady=10)

        cuerpo = ttk.Frame(self.main_frame, style="TFrame")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=12)

        self.notebook = ttk.Notebook(cuerpo)
        self.notebook.pack(fill="both", expand=True)

        self.tab_parametros = ttk.Frame(self.notebook, style="TFrame")
        self.tab_vector = ttk.Frame(self.notebook, style="TFrame")
        self.tab_metricas = ttk.Frame(self.notebook, style="TFrame")
        self.tab_rk = ttk.Frame(self.notebook, style="TFrame")
        self.tab_15min = ttk.Frame(self.notebook, style="TFrame")

        self.notebook.add(self.tab_parametros, text="⚙  Parámetros")
        self.notebook.add(self.tab_vector, text="📋  Vector de Estado")
        self.notebook.add(self.tab_metricas, text="📊  Métricas")
        self.notebook.add(self.tab_rk, text="🧮  Runge-Kutta")
        self.notebook.add(self.tab_15min, text="🕒  Salas / 15 min")

        self._armar_tab_parametros()
        self._armar_tab_vector()
        self._armar_tab_metricas()
        self._armar_tab_rk()
        self._armar_tab_15min()

        # Barra de estado
        self.lbl_estado = tk.Label(self.main_frame, text="Listo para simular. Configurá los parámetros y presioná Iniciar.",
                                    bg=COLOR_DORADO, fg="white", font=("Segoe UI", 9), anchor="w")
        self.lbl_estado.pack(fill="x", side="bottom")

    # ------------------------------------------------------------------
    # TAB 1: Parámetros
    # ------------------------------------------------------------------
    def _armar_tab_parametros(self):
        contenedor = ttk.Frame(self.tab_parametros, style="TFrame")
        contenedor.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(contenedor, text="Configuración del sistema", style="Titulo.TLabel").pack(anchor="w", pady=(0, 14))

        # --- Panel de Puertas ---
        frame_puertas = self._crear_panel(contenedor, "Llegadas por puerta (Media, Desviación) — Distribución Normal, segundos")
        self._fila_param(frame_puertas, 0, "Puerta A (desde 9 hs):", self.media_a, self.desv_a)
        self._fila_param(frame_puertas, 1, "Puerta B (desde 11 hs):", self.media_b, self.desv_b)
        self._fila_param(frame_puertas, 2, "Puerta C (desde 14 hs):", self.media_c, self.desv_c)

        # --- Panel de Cerveza y probabilidades ---
        frame_cerveza = self._crear_panel(contenedor, "Stand de cerveza, Informes y Probabilidades")
        
        ttk.Label(frame_cerveza, text="Atención Folletos (media, desv seg):", style="Panel.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_cerveza, textvariable=self.folletos_media, width=8).grid(row=0, column=1, padx=4)
        ttk.Entry(frame_cerveza, textvariable=self.folletos_desv, width=8).grid(row=0, column=2, padx=4)

        ttk.Label(frame_cerveza, text="Servicio cerveza (min, max seg):", style="Panel.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_cerveza, textvariable=self.cerveza_min, width=8).grid(row=1, column=1, padx=4)
        ttk.Entry(frame_cerveza, textvariable=self.cerveza_max, width=8).grid(row=1, column=2, padx=4)
        
        ttk.Label(frame_cerveza, text="Edad media cerveza (años):", style="Panel.TLabel").grid(row=1, column=3, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_cerveza, textvariable=self.edad_media, width=8).grid(row=1, column=4, padx=4)

        ttk.Label(frame_cerveza, text="% que pide folletos:", style="Panel.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_cerveza, textvariable=self.prob_folletos, width=8).grid(row=2, column=1, padx=4)

        ttk.Label(frame_cerveza, text="% que va a Fotografía tras Pintura:", style="Panel.TLabel").grid(row=3, column=0, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_cerveza, textvariable=self.prob_fotografia, width=8).grid(row=3, column=1, padx=4)

        ttk.Label(frame_cerveza, text="% que degusta cerveza (de los que van a Foto):", style="Panel.TLabel").grid(row=4, column=0, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_cerveza, textvariable=self.prob_cerveza, width=8).grid(row=4, column=1, padx=4)

        # --- Panel de control de simulación ---
        frame_control = self._crear_panel(contenedor, "Control de la simulación y Parámetros Extra")
        
        ttk.Label(frame_control, text="Mostrar desde iteración (j):", style="Panel.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_control, textvariable=self.param_j, width=10).grid(row=0, column=1, padx=4)

        ttk.Label(frame_control, text="Cant. de iteraciones a mostrar (i):", style="Panel.TLabel").grid(row=0, column=2, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_control, textvariable=self.param_i, width=10).grid(row=0, column=3, padx=4)

        ttk.Label(frame_control, text="Días a simular:", style="Panel.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_control, textvariable=self.param_dias, width=10).grid(row=1, column=1, padx=4)

        ttk.Label(frame_control, text="Tope de iteraciones (máx 100k):", style="Panel.TLabel").grid(row=1, column=2, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_control, textvariable=self.param_iter_max, width=10).grid(row=1, column=3, padx=4)

        ttk.Label(frame_control, text="Instante X de corte (segundos, 0=ignorar):", style="Panel.TLabel").grid(row=2, column=0, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_control, textvariable=self.param_x, width=10).grid(row=2, column=1, padx=4)

        ttk.Label(frame_control, text="Paso (h) para Runge-Kutta:", style="Panel.TLabel").grid(row=2, column=2, sticky="w", padx=10, pady=6)
        ttk.Entry(frame_control, textvariable=self.param_h, width=10).grid(row=2, column=3, padx=4)

        ttk.Label(frame_control, text="Distribución para Salas:", style="Panel.TLabel").grid(row=3, column=0, sticky="w", padx=10, pady=6)
        cb_dist = ttk.Combobox(frame_control, textvariable=self.dist_salas, values=["Normal", "Uniforme"], state="readonly", width=12)
        cb_dist.grid(row=3, column=1, padx=4)

        # --- Panel de Tiempos de Salas ---
        frame_salas = self._crear_panel(contenedor, "Tiempos en Salas por Horario (Media, Desv)")
        ttk.Label(frame_salas, text="Pintura", style="Subtitulo.TLabel").grid(row=0, column=1, columnspan=2, pady=2)
        ttk.Label(frame_salas, text="Fotografía", style="Subtitulo.TLabel").grid(row=0, column=3, columnspan=2, pady=2)
        
        horarios = ["9 a 12 hs", "12 a 14 hs", "14 a 18 hs", "18 a 22 hs"]
        vars_pint = [(self.salas_pint_m1, self.salas_pint_d1), (self.salas_pint_m2, self.salas_pint_d2), 
                     (self.salas_pint_m3, self.salas_pint_d3), (self.salas_pint_m4, self.salas_pint_d4)]
        vars_foto = [(self.salas_foto_m1, self.salas_foto_d1), (self.salas_foto_m2, self.salas_foto_d2), 
                     (self.salas_foto_m3, self.salas_foto_d3), (self.salas_foto_m4, self.salas_foto_d4)]
        
        for i, (h, vp, vf) in enumerate(zip(horarios, vars_pint, vars_foto)):
            ttk.Label(frame_salas, text=h, style="Panel.TLabel").grid(row=i+1, column=0, padx=10)
            ttk.Entry(frame_salas, textvariable=vp[0], width=6).grid(row=i+1, column=1, padx=2)
            ttk.Entry(frame_salas, textvariable=vp[1], width=6).grid(row=i+1, column=2, padx=(2, 20))
            ttk.Entry(frame_salas, textvariable=vf[0], width=6).grid(row=i+1, column=3, padx=2)
            ttk.Entry(frame_salas, textvariable=vf[1], width=6).grid(row=i+1, column=4, padx=2)

        btn_simular = ttk.Button(contenedor, text="▶  Iniciar Simulación", style="Accion.TButton",
                                  command=self.ejecutar_simulacion)
        btn_simular.pack(pady=18)

    def _crear_panel(self, parent, titulo):
        """Crea un Labelframe con un borde sutil alrededor, usado como
        contenedor visual para cada grupo de parámetros."""
        outer = tk.Frame(parent, bg=COLOR_BORDE, padx=1, pady=1)
        outer.pack(fill="x", pady=8)
        frame = ttk.Labelframe(outer, text=titulo, style="TLabelframe")
        frame.pack(fill="x")
        return frame

    def _fila_param(self, frame, row, etiqueta, var_media, var_desv):
        ttk.Label(frame, text=etiqueta, style="Panel.TLabel", width=26).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        ttk.Label(frame, text="Media:", style="Panel.TLabel").grid(row=row, column=1, sticky="e")
        ttk.Entry(frame, textvariable=var_media, width=8).grid(row=row, column=2, padx=4)
        ttk.Label(frame, text="Desv:", style="Panel.TLabel").grid(row=row, column=3, sticky="e")
        ttk.Entry(frame, textvariable=var_desv, width=8).grid(row=row, column=4, padx=4)

    # ------------------------------------------------------------------
    # TAB 2: Vector de estado (detalle completo por visitante)
    # ------------------------------------------------------------------
    def _armar_tab_vector(self):
        contenedor = ttk.Frame(self.tab_vector, style="TFrame")
        contenedor.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(contenedor, text="Vector de estado", style="Titulo.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(contenedor,
                  text="Seleccioná una fila para ver el detalle completo de cada visitante activo en ese instante (atributos y RNDs usados).",
                  style="TLabel", wraplength=900).pack(anchor="w", pady=(0, 8))

        panel_split = ttk.Frame(contenedor, style="TFrame")
        panel_split.pack(fill="both", expand=True)

        # --- Controles Superiores ---
        frame_controles = ttk.Frame(panel_split, style="TFrame")
        frame_controles.pack(side="top", fill="x", pady=(0, 10))

        ttk.Label(frame_controles, text="Desde iteración (j):", style="Panel.TLabel").pack(side="left", padx=(0, 5))
        ttk.Entry(frame_controles, textvariable=self.param_j, width=10).pack(side="left", padx=5)

        ttk.Label(frame_controles, text="Cantidad a mostrar (i):", style="Panel.TLabel").pack(side="left", padx=(20, 5))
        ttk.Entry(frame_controles, textvariable=self.param_i, width=10).pack(side="left", padx=5)

        ttk.Button(frame_controles, text="Actualizar Vista", style="Accion.TButton", command=self.actualizar_vista_vector).pack(side="left", padx=20)

        # --- Tabla principal (iteraciones) ---
        frame_tabla = ttk.Frame(panel_split, style="TFrame")
        frame_tabla.pack(side="top", fill="both", expand=True)

        columnas = ('Iteracion', 'Dia', 'Hora', 'Reloj_Global', 'Evento',
                    'ProxA', 'RNDA', 'ProxB', 'RNDB', 'ProxC', 'RNDC',
                    'ColaV1', 'ColaV2', 'Pintura', 'ColaCerveza', 'ServLibres', 'Fotografia', 'Activos')
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=14)
        encabezados = {
            'Iteracion': 'Iter.', 'Dia': 'Día', 'Hora': 'Hora', 'Reloj_Global': 'Reloj (s)',
            'Evento': 'Evento', 
            'ProxA': 'Próx. A', 'RNDA': 'RND L. A', 'ProxB': 'Próx. B', 'RNDB': 'RND L. B', 'ProxC': 'Próx. C', 'RNDC': 'RND L. C',
            'ColaV1': 'Cola V1', 'ColaV2': 'Cola V2', 'Pintura': 'En Pintura',
            'ColaCerveza': 'Cola Cerveza', 'ServLibres': 'Serv. Libres', 'Fotografia': 'En Fotografía',
            'Activos': '# Activos'
        }
        anchos = {'Iteracion': 50, 'Dia': 40, 'Hora': 65, 'Reloj_Global': 80, 'Evento': 170,
                  'ProxA': 65, 'RNDA': 80, 'ProxB': 65, 'RNDB': 80, 'ProxC': 65, 'RNDC': 80,
                  'ColaV1': 65, 'ColaV2': 65, 'Pintura': 75, 'ColaCerveza': 90, 'ServLibres': 85,
                  'Fotografia': 90, 'Activos': 70}
        for col in columnas:
            self.tree.heading(col, text=encabezados[col])
            self.tree.column(col, width=anchos[col], anchor="center")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._mostrar_detalle_fila)

        # --- Panel de detalle de visitantes de la fila seleccionada ---
        frame_detalle = ttk.Labelframe(panel_split, text="Detalle de visitantes activos en la fila seleccionada", style="TLabelframe")
        frame_detalle.pack(side="bottom", fill="both", expand=False, pady=(10, 0))

        columnas_det = ('ID', 'Puerta', 'Edad', 'RND_Edad', 'Estado', 'Sala', 'Llegada', 
                        'RND_Foll', 'RND_Vent', 'RND_T_Foll', 'RND_T_Pint', 'RND_Foto', 'RND_Cerv', 'RND_T_Cerv','RND_T_Foto')
        self.tree_detalle = ttk.Treeview(frame_detalle, columns=columnas_det, show='headings', height=8)
        for col in columnas_det:
            self.tree_detalle.heading(col, text=col)
            # Achicamos un poco el ancho para que entren
            self.tree_detalle.column(col, width=80, anchor="center")
        scroll_det = ttk.Scrollbar(frame_detalle, orient="vertical", command=self.tree_detalle.yview)
        self.tree_detalle.configure(yscrollcommand=scroll_det.set)
        self.tree_detalle.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scroll_det.pack(side="right", fill="y", pady=8)

        self._filas_guardadas = []  # cache para poder reconstruir el detalle al seleccionar

    def _mostrar_detalle_fila(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        idx = self.tree.index(seleccion[0])
        if idx >= len(self._filas_guardadas):
            return
        fila = self._filas_guardadas[idx]

        for row in self.tree_detalle.get_children():
            self.tree_detalle.delete(row)

        for vis in fila.get('Visitantes_Activos_Detalle', []):
            self.tree_detalle.insert('', 'end', values=(
                vis['ID'], vis['Puerta'], vis['Edad'], vis['RND_Edad'],
                vis['Estado'], vis['Sala'], vis['Llegada'],
                vis.get('RND_Dec_Folletos', ''), vis.get('RND_Vent_Elegida', ''),
                vis.get('RND_Tiempo_Foll', ''), vis.get('RND_Tiempo_Pintura', ''),
                vis.get('RND_Dec_Foto', ''), vis.get('RND_Dec_Cerveza', ''),
                vis.get('RND_Tiempo_Cerveza', ''),
                vis.get('RND_Tiempo_Foto', '')
            ))

    def actualizar_vista_vector(self):
        if not hasattr(self, 'todas_las_filas_simulacion'):
            messagebox.showinfo("Atención", "Primero debés ejecutar una simulación.")
            return
            
        j_str = self.param_j.get().strip()
        if not j_str.isdigit():
            messagebox.showerror("Error", "El valor de j debe ser un número entero.")
            return
        desde_j = int(j_str)
        
        i_str = self.param_i.get().strip()
        if i_str == "":
            cantidad_i = float('inf')
        elif not i_str.isdigit():
            messagebox.showerror("Error", "El valor de i debe ser un número entero o estar vacío.")
            return
        else:
            cantidad_i = int(i_str)

        for row in self.tree.get_children():
            self.tree.delete(row)
            
        filas_a_mostrar = [
            f for f in self.todas_las_filas_simulacion 
            if desde_j <= f['Iteracion'] <= (desde_j + cantidad_i)
        ]
        
        self._filas_guardadas = filas_a_mostrar
        for fila in filas_a_mostrar:
            self.tree.insert('', 'end', values=(
                fila['Iteracion'], fila['Dia'], fila['Hora_Aprox'], fila['Reloj_Global'], fila['Evento'],
                fila.get('Prox_Lleg_A', ''), fila.get('RND_Lleg_A', ''),
                fila.get('Prox_Lleg_B', ''), fila.get('RND_Lleg_B', ''),
                fila.get('Prox_Lleg_C', ''), fila.get('RND_Lleg_C', ''),
                fila['En_Cola_Informes_V1'], fila['En_Cola_Informes_V2'], fila['En_Pintura'],
                fila['En_Cola_Cerveza'], fila['Servidores_Cerveza_Libres'], fila['En_Fotografia'],
                fila['Cantidad_Visitantes_Activos']
            ))

        for row in self.tree_detalle.get_children():
            self.tree_detalle.delete(row)
    # ------------------------------------------------------------------
    # TAB 3: Métricas
    # ------------------------------------------------------------------
    def _armar_tab_metricas(self):
        contenedor = ttk.Frame(self.tab_metricas, style="TFrame")
        contenedor.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(contenedor, text="Resultados de la simulación", style="Titulo.TLabel").pack(anchor="w", pady=(0, 14))

        self.frame_obligatorias = ttk.Labelframe(contenedor, text="Métricas obligatorias", style="TLabelframe")
        self.frame_obligatorias.pack(fill="x", pady=8)

        self.frame_extra = ttk.Labelframe(contenedor, text="5 métricas adicionales", style="TLabelframe")
        self.frame_extra.pack(fill="x", pady=8)

        self.lbl_placeholder = ttk.Label(contenedor, text="Ejecutá la simulación en la pestaña Parámetros para ver resultados aquí.",
                                          style="TLabel")
        self.lbl_placeholder.pack(anchor="w", pady=10)

    def _fila_metrica(self, frame, row, etiqueta, valor):
        ttk.Label(frame, text=etiqueta, style="Metrica.TLabel").grid(row=row, column=0, sticky="w", padx=14, pady=8)
        ttk.Label(frame, text=valor, style="MetricaValor.TLabel").grid(row=row, column=1, sticky="w", padx=14, pady=8)

    def _actualizar_metricas(self, metricas):
        for w in self.frame_obligatorias.winfo_children():
            w.destroy()
        for w in self.frame_extra.winfo_children():
            w.destroy()
        self.lbl_placeholder.pack_forget()

        self._fila_metrica(self.frame_obligatorias, 0, "Tiempo promedio de permanencia en la exposición:",
                            f"{metricas['prom_permanencia']:.2f} seg")
        self._fila_metrica(self.frame_obligatorias, 1, "Tiempo promedio en cola V1:",
                            f"{metricas.get('prom_cola_v1', 0):.2f} seg")
        self._fila_metrica(self.frame_obligatorias, 2, "Tiempo promedio en cola V2:",
                            f"{metricas.get('prom_cola_v2', 0):.2f} seg")
        self._fila_metrica(self.frame_obligatorias, 3, "Visitantes totales ingresados:",
                            f"{metricas['visitantes_totales']}")
        self._fila_metrica(self.frame_obligatorias, 4, "Visitantes que finalizaron su recorrido:",
                            f"{metricas['visitantes_finalizados']}")

        self._fila_metrica(self.frame_extra, 0, "1. Total de visitantes que solicitaron folletos:",
                            f"{metricas['total_folletos']}")
        self._fila_metrica(self.frame_extra, 1, "2. Edad promedio de quienes degustaron cerveza:",
                            f"{metricas['prom_edad_cerveza']:.1f} años")
        self._fila_metrica(self.frame_extra, 2, "3. Máxima longitud alcanzada en cola de cerveza:",
                            f"{metricas.get('max_cola_cerveza', 0)}")
        self._fila_metrica(self.frame_extra, 3, "4. Total de visitantes que entraron a Fotografía:",
                            f"{metricas['total_fotografia']}")
        self._fila_metrica(self.frame_extra, 4, "5. Personas que abandonaron tras Pintura (no fueron a Foto):",
                            f"{metricas['abandonos_post_pintura']}")
        

    # ------------------------------------------------------------------
    # TAB 4: Runge-Kutta
    # ------------------------------------------------------------------
    def _armar_tab_rk(self):
        contenedor = ttk.Frame(self.tab_rk, style="TFrame")
        contenedor.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(contenedor, text="Tablas de Runge-Kutta — Tiempo de degustación de cerveza",
                  style="Titulo.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(contenedor, text="dC/dt = (t² − C) · h²   con h = 0.05, C(0) = edad del visitante",
                  style="TLabel", font=("Consolas", 10, "italic")).pack(anchor="w", pady=(0, 10))

        panel = ttk.Frame(contenedor, style="TFrame")
        panel.pack(fill="both", expand=True)

        # Lista de visitantes a la izquierda
        frame_lista = ttk.Labelframe(panel, text="Visitantes que degustaron", style="TLabelframe", width=260)
        frame_lista.pack(side="left", fill="y", padx=(0, 10))

        self.lista_rk = tk.Listbox(frame_lista, width=34, height=28, font=FUENTE_TEXTO,
                                    bg="white", fg=COLOR_TEXTO, selectbackground=COLOR_BORGOÑA,
                                    selectforeground="white", borderwidth=0, highlightthickness=0)
        self.lista_rk.pack(fill="both", expand=True, padx=8, pady=8)
        self.lista_rk.bind("<<ListboxSelect>>", self._mostrar_tabla_rk_seleccionada)

        # Tabla de la derecha
        frame_tabla_rk = ttk.Labelframe(panel, text="Pasos calculados", style="TLabelframe")
        frame_tabla_rk.pack(side="left", fill="both", expand=True)

        self.tree_rk = ttk.Treeview(frame_tabla_rk, columns=('t', 'C', 'dCdt', 'k1', 'k2', 'k3', 'k4'), show='headings')
        self.tree_rk.heading('t', text='t')
        self.tree_rk.heading('C', text='C(t)')
        self.tree_rk.heading('dCdt', text='dC/dt')
        self.tree_rk.heading('k1', text='k1')
        self.tree_rk.heading('k2', text='k2')
        self.tree_rk.heading('k3', text='k3')
        self.tree_rk.heading('k4', text='k4')
        for c in ('t', 'C', 'dCdt', 'k1', 'k2', 'k3', 'k4'):
            self.tree_rk.column(c, width=100, anchor="center")
        scroll_rk = ttk.Scrollbar(frame_tabla_rk, orient="vertical", command=self.tree_rk.yview)
        self.tree_rk.configure(yscrollcommand=scroll_rk.set)
        self.tree_rk.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        scroll_rk.pack(side="right", fill="y", pady=8)

        self._tablas_rk_dict = {}

    def _mostrar_tabla_rk_seleccionada(self, event):
        seleccion = self.lista_rk.curselection()
        if not seleccion:
            return
        clave = self.lista_rk.get(seleccion[0])
        tabla = self._tablas_rk_dict.get(clave)
        if tabla is None:
            return

        for row in self.tree_rk.get_children():
            self.tree_rk.delete(row)

        for _, fila in tabla.iterrows():
            self.tree_rk.insert('', 'end', values=(fila['t'], fila['C(t)'], fila['dC/dt'], fila['k1'], fila['k2'], fila['k3'], fila['k4']))

    def _actualizar_rk(self, tablas_dict):
        self.lista_rk.delete(0, tk.END)
        self._tablas_rk_dict = tablas_dict
        for clave in tablas_dict.keys():
            self.lista_rk.insert(tk.END, clave)

    # ------------------------------------------------------------------
    # TAB 5: Salas cada 15 minutos (tabla )
    # ------------------------------------------------------------------
    def _armar_tab_15min(self):
        contenedor = ttk.Frame(self.tab_15min, style="TFrame")
        contenedor.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(contenedor, text="Personas en sala cada 15 minutos", style="Titulo.TLabel").pack(anchor="w", pady=(0, 8))

        # Panel único para la tabla (sin división para el gráfico)
        frame_tabla = ttk.Frame(contenedor, style="TFrame")
        frame_tabla.pack(fill="both", expand=True)

        self.tree_15 = ttk.Treeview(frame_tabla, columns=('Dia', 'Hora', 'Pintura', 'Foto'), show='headings', height=22)
        self.tree_15.heading('Dia', text='Día')
        self.tree_15.heading('Hora', text='Hora')
        self.tree_15.heading('Pintura', text='En Pintura')
        self.tree_15.heading('Foto', text='En Fotografía')
        
        for c in ('Dia', 'Hora', 'Pintura', 'Foto'):
            self.tree_15.column(c, width=150, anchor="center")
            
        scroll_15 = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree_15.yview)
        self.tree_15.configure(yscrollcommand=scroll_15.set)
        
        self.tree_15.pack(side="left", fill="both", expand=True)
        scroll_15.pack(side="right", fill="y")

    def _actualizar_15min(self, metricas_15):
        # Limpiar tabla
        for row in self.tree_15.get_children():
            self.tree_15.delete(row)
            
        # Insertar nuevas filas
        for m in metricas_15:
            self.tree_15.insert('', 'end', values=(m['Dia'], m['Hora'], m['En_Pintura'], m['En_Fotografia']))

    # ------------------------------------------------------------------
    # Ejecutar la simulación y refrescar todas las pestañas
    # ------------------------------------------------------------------
    def ejecutar_simulacion(self):
        try:
            parametros = {
                'puerta_a': (self.media_a.get(), self.desv_a.get()),
                'puerta_b': (self.media_b.get(), self.desv_b.get()),
                'puerta_c': (self.media_c.get(), self.desv_c.get()),
                'cerveza': (self.cerveza_min.get(), self.cerveza_max.get()),
                'folletos': (self.folletos_media.get(), self.folletos_desv.get()),
                'edad_media': self.edad_media.get(),
                'salas': {
                    'Pintura': {
                        '9_12': (self.salas_pint_m1.get(), self.salas_pint_d1.get()),
                        '12_14': (self.salas_pint_m2.get(), self.salas_pint_d2.get()),
                        '14_18': (self.salas_pint_m3.get(), self.salas_pint_d3.get()),
                        '18_22': (self.salas_pint_m4.get(), self.salas_pint_d4.get())
                    },
                    'Fotografia': {
                        '9_12': (self.salas_foto_m1.get(), self.salas_foto_d1.get()),
                        '12_14': (self.salas_foto_m2.get(), self.salas_foto_d2.get()),
                        '14_18': (self.salas_foto_m3.get(), self.salas_foto_d3.get()),
                        '18_22': (self.salas_foto_m4.get(), self.salas_foto_d4.get())
                    }
                },
                'dias': max(1, self.param_dias.get()),
                'prob_folletos': self.prob_folletos.get() / 100.0,
                'prob_fotografia': self.prob_fotografia.get() / 100.0,
                'prob_cerveza': self.prob_cerveza.get() / 100.0,
                'tiempo_x': self.param_x.get(),
                'rk_h': self.param_h.get(),
                'dist_salas': self.dist_salas.get()
            }
        except tk.TclError:
            messagebox.showerror("Error", "Revisá que todos los parámetros sean números válidos.")
            return

        iter_max = min(100000, max(1, self.param_iter_max.get()))

        j_str = self.param_j.get().strip()
        if not j_str.isdigit():
            messagebox.showerror("Error", "El valor de j debe ser un número entero.")
            return
        param_j_val = int(j_str)

        i_str = self.param_i.get().strip()
        if i_str == "":
            param_i_val = 9999999
        elif not i_str.isdigit():
            messagebox.showerror("Error", "El valor de i debe ser un número entero o estar vacío.")
            return
        else:
            param_i_val = int(i_str)

        self.lbl_estado.config(text="Simulando... esto puede tardar unos segundos.")
        self.root.update_idletasks()

        self.simulador_actual = Simulador(parametros)
        resultados = self.simulador_actual.simular(iter_max, param_j_val, param_i_val)

        self.todas_las_filas_simulacion = resultados
        self.actualizar_vista_vector()

        # --- Métricas ---
        metricas = self.simulador_actual.obtener_metricas()
        self._actualizar_metricas(metricas)

        # --- Runge-Kutta ---
        self._actualizar_rk(self.simulador_actual.tablas_rk_generadas)

        # --- 15 minutos ---
        self._actualizar_15min(self.simulador_actual.metricas_15_min)

        self.lbl_estado.config(
            text=f"Simulación completa — {self.simulador_actual.visitantes_totales} visitantes, "
                 f"{len(resultados)} filas mostradas, {self.simulador_actual.dia_actual} día(s) simulado(s)."
        )
