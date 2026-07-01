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
        # NOTA IMPORTANTE: antes toda la ventana (header + pestañas + barra de
        # estado) estaba metida dentro de un Canvas "gigante" con scroll. El
        # problema real era otro: un ttk.Notebook se dimensiona para poder
        # mostrar SIEMPRE la pestaña más grande de todas (aunque no esté
        # visible). Como la tabla de "Vector de Estado" tiene ~65 columnas
        # anchas, el Notebook entero pedía un ancho enorme (varios miles de
        # píxeles), y eso empujaba el botón "Iniciar Simulación" fuera de la
        # pantalla y dejaba columnas de la tabla inalcanzables. Se corrige
        # "aislando" cada pestaña (ver `.pack_propagate(False)` más abajo) y
        # dándole scroll propio solo a la pestaña de Parámetros, que es la
        # que puede llegar a no entrar completa en pantallas chicas.
        header = tk.Frame(self.root, bg=COLOR_BORGOÑA, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="🏛  PALACIO FERREYRA", bg=COLOR_BORGOÑA, fg="white",
                 font=("Georgia", 18, "bold")).pack(side="left", padx=20, pady=10)
        tk.Label(header, text="Simulador de eventos discretos — TP5 Simulación 2026",
                 bg=COLOR_BORGOÑA, fg="#EBD9D9", font=("Segoe UI", 10, "italic")).pack(side="left", pady=10)

        # Barra de estado: se empaqueta ANTES que el cuerpo expandible para
        # asegurar que siempre reserve su espacio abajo y nunca desaparezca.
        self.lbl_estado = tk.Label(self.root, text="Listo para simular. Configurá los parámetros y presioná Iniciar.",
                                    bg=COLOR_DORADO, fg="white", font=("Segoe UI", 9), anchor="w")
        self.lbl_estado.pack(fill="x", side="bottom")

        cuerpo = ttk.Frame(self.root, style="TFrame")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=12)

        self.notebook = ttk.Notebook(cuerpo)
        self.notebook.pack(fill="both", expand=True)

        self.tab_parametros = ttk.Frame(self.notebook, style="TFrame")
        self.tab_vector = ttk.Frame(self.notebook, style="TFrame")
        self.tab_metricas = ttk.Frame(self.notebook, style="TFrame")
        self.tab_rk = ttk.Frame(self.notebook, style="TFrame")
        self.tab_15min = ttk.Frame(self.notebook, style="TFrame")

        # Evita que cada pestaña "infle" el tamaño pedido por el Notebook
        # según el contenido de SUS hijos (esto es lo que causaba la
        # ventana gigante). El tamaño real que ocupan lo sigue dando el
        # propio Notebook (fill=both, expand=True) en tiempo de ejecución.
        for tab in (self.tab_parametros, self.tab_vector, self.tab_metricas,
                    self.tab_rk, self.tab_15min):
            tab.pack_propagate(False)

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

    # ------------------------------------------------------------------
    # Helper: convierte cualquier `parent` en un área con scroll vertical
    # propio (canvas + scrollbar + rueda del mouse). Se usa en la pestaña
    # de Parámetros para que, sin importar el tamaño de la ventana, siempre
    # se pueda bajar hasta ver (y usar) el botón "Iniciar Simulación".
    # ------------------------------------------------------------------
    def _crear_area_scrollable(self, parent):
        wrapper = ttk.Frame(parent, style="TFrame")
        wrapper.pack(fill="both", expand=True)

        canvas = tk.Canvas(wrapper, bg=COLOR_FONDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
        frame_interior = ttk.Frame(canvas, style="TFrame", padding=20)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        window_id = canvas.create_window((0, 0), window=frame_interior, anchor="nw")

        def _actualizar_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _ajustar_ancho(event):
            canvas.itemconfigure(window_id, width=event.width)

        frame_interior.bind("<Configure>", _actualizar_scrollregion)
        canvas.bind("<Configure>", _ajustar_ancho)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_wheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_wheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)

        return frame_interior

    # ------------------------------------------------------------------
    # TAB 1: Parámetros
    # ------------------------------------------------------------------
    def _armar_tab_parametros(self):
        contenedor = self._crear_area_scrollable(self.tab_parametros)

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
        ttk.Label(frame_control, text="Normal (fija)", style="Panel.TLabel",
                  font=("Segoe UI", 9, "bold")).grid(row=3, column=1, sticky="w", padx=4)

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
    # Cantidad de "columnas de visitante" (Estado + Hora de llegada) que
    # se agregan al final de la planilla, una por cada visitante presente
    # en el sistema en ese instante (Visitante 1, Visitante 2, ...). Si en
    # algún evento hay más visitantes activos que columnas disponibles, la
    # última columna avisa "+N más" en vez de cortar la info sin aviso.
    MAX_VISITANTES_MOSTRADOS = 20

    # Definición de columnas de la planilla del vector de estado: cada
    # tupla es (clave_en_la_fila, encabezado, ancho_px). Es UNA sola tabla
    # con una fila por evento, igual que una planilla armada a mano.
    COLUMNAS_VECTOR = [
        ('Iteracion', 'N°', 45),
        ('Dia', 'Día', 35),
        # "Hora" y "Reloj" mostraban lo mismo (el reloj de la simulación),
        # solo que uno en formato HH:MM:SS y el otro en segundos. Se deja
        # una sola columna (Reloj, en segundos) para no repetir información.
        ('Reloj_Global', 'Reloj (seg)', 80),
        ('Evento', 'Evento', 160),

        ('RND1_LlegA', 'RND1 Lleg.A', 75), ('RND2_LlegA', 'RND2 Lleg.A', 75),
        ('TEntreLlegA', 'T.entre Lleg.A', 85), ('ProxLlegA', 'Próx Lleg.A', 80),
        ('RND1_LlegB', 'RND1 Lleg.B', 75), ('RND2_LlegB', 'RND2 Lleg.B', 75),
        ('TEntreLlegB', 'T.entre Lleg.B', 85), ('ProxLlegB', 'Próx Lleg.B', 80),
        ('RND1_LlegC', 'RND1 Lleg.C', 75), ('RND2_LlegC', 'RND2 Lleg.C', 75),
        ('TEntreLlegC', 'T.entre Lleg.C', 85), ('ProxLlegC', 'Próx Lleg.C', 80),

        ('RND_Informes', 'RND Informes', 80), ('Informe', 'Informe SI/NO', 85),
        ('RND_EligeVent', 'RND Elige Vent', 90), ('Ventanilla', 'Ventanilla Elegida', 100),
        ('ColaV1', 'Cola V1', 55), ('ColaV2', 'Cola V2', 55),

        ('V1E1_Estado', 'V1-Emp1 Estado', 120), ('V1E1_Fin', 'V1-Emp1 Fin At.', 80),
        ('V1E2_Estado', 'V1-Emp2 Estado', 120), ('V1E2_Fin', 'V1-Emp2 Fin At.', 80),
        ('V2E1_Estado', 'V2-Emp1 Estado', 120), ('V2E1_Fin', 'V2-Emp1 Fin At.', 80),
        ('V2E2_Estado', 'V2-Emp2 Estado', 120), ('V2E2_Fin', 'V2-Emp2 Fin At.', 80),

        ('RND_T_Foll', 'RND T.Folletos', 85), ('T_Foll', 'T.Folletos', 70), ('Fin_Foll', 'Fin Folletos', 80),

        ('PersPintura', 'Personas Pintura', 90),
        ('RND_T_Pint', 'RND T.Pintura', 110), ('T_Pint', 'T.Pintura', 70), ('Fin_Pint', 'Fin Pintura', 80),

        ('RND_VaFoto', 'RND Va Foto?', 80), ('VaFoto', 'Va Foto SI/NO', 85),
        ('PersFoto', 'Personas Foto', 85),
        ('RND_T_Foto', 'RND T.Foto', 100), ('T_Foto', 'T.Foto', 65), ('Fin_Foto', 'Fin Foto', 80),

        ('RND_Edad', 'RND Edad', 65), ('Edad', 'Edad (Trunc)', 75), ('EsMayorEdad', 'Es Mayor de Edad', 100),
        ('RND_TomaBirra', 'RND Toma Birra?', 90), ('TomaBirra', 'Toma Birra SI/NO', 110),
        ('ColaStand', 'Cola Stand', 70),
        ('CervE1_Estado', 'Cerv-Serv1 Estado', 130), ('CervE1_Fin', 'Cerv-Serv1 Fin At.', 85),
        ('CervE2_Estado', 'Cerv-Serv2 Estado', 130), ('CervE2_Fin', 'Cerv-Serv2 Fin At.', 85),
        ('RND_TpoServ', 'RND Tpo Servir', 85), ('TpoServ', 'Tpo Servir', 70), ('TpoTomarRK', 'Tpo Tomar (RK)', 90),

        ('ProxControl15', 'Próx Control 15m', 100),
        ('Reg15Pint', 'Reg 15m Pint.', 80), ('Reg15Foto', 'Reg 15m Foto', 80),

        ('AC_EsperaV1', 'AC Espera V1', 85), ('ContClientesV1', 'Cont. Clientes V1', 90),
        ('AC_EsperaV2', 'AC Espera V2', 85), ('ContClientesV2', 'Cont. Clientes V2', 90),
        ('AC_Permanencia', 'AC T.Permanencia', 100), ('ContSalen', 'Cont. Visit. Salen', 95),
        ('ContBirras', 'Cont. Birras', 75), ('AC_Edades', 'AC Edades Birra', 90),
        ('ContDirecto', 'Cont. Directo Muestra', 100),
    ]

    # Después de los contadores/acumuladores, va el detalle de cada
    # visitante presente en el sistema en ese instante: "Visitante 1"
    # (Estado + Hora de llegada), "Visitante 2", etc.
    for _i in range(1, MAX_VISITANTES_MOSTRADOS + 1):
        COLUMNAS_VECTOR.append((f'Vis{_i}_Estado', f'Visitante {_i} - Estado', 130))
        COLUMNAS_VECTOR.append((f'Vis{_i}_Llegada', f'Visitante {_i} - H.Llegada', 95))
    del _i

    def _armar_tab_vector(self):
        contenedor = ttk.Frame(self.tab_vector, style="TFrame")
        contenedor.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(contenedor, text="Vector de estado", style="Titulo.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(contenedor,
                  text="Una fila por evento, con todos los números aleatorios, estados de empleados/colas y acumuladores "
                       "usados en ese instante (las columnas transitorias quedan en blanco cuando no corresponden a ese evento). "
                       f"Al final de la planilla se listan hasta {self.MAX_VISITANTES_MOSTRADOS} visitantes activos "
                       "(Visitante 1, Visitante 2, ...) con su Estado y Hora de llegada. "
                       "Desplazate horizontalmente (o Shift + rueda del mouse) para ver todas las columnas.",
                  style="TLabel", wraplength=1100).pack(anchor="w", pady=(0, 8))

        # --- Controles Superiores ---
        frame_controles = ttk.Frame(contenedor, style="TFrame")
        frame_controles.pack(side="top", fill="x", pady=(0, 10))

        ttk.Label(frame_controles, text="Desde iteración (j):", style="Panel.TLabel").pack(side="left", padx=(0, 5))
        ttk.Entry(frame_controles, textvariable=self.param_j, width=10).pack(side="left", padx=5)

        ttk.Label(frame_controles, text="Cantidad a mostrar (i):", style="Panel.TLabel").pack(side="left", padx=(20, 5))
        ttk.Entry(frame_controles, textvariable=self.param_i, width=10).pack(side="left", padx=5)

        ttk.Button(frame_controles, text="Actualizar Vista", style="Accion.TButton", command=self.actualizar_vista_vector).pack(side="left", padx=10)
        ttk.Button(frame_controles, text="Ver Estado Gráfico", style="Accion.TButton", command=self.abrir_visualizacion_grafica).pack(side="left", padx=10)

        # --- Tabla única (planilla completa) ---
        # OJO: frame_tabla usa pack_propagate(False) a propósito. Sin esto,
        # el Treeview (que tiene ~65 columnas y pide más de 5000px de ancho
        # para mostrarlas todas sin scroll) infla el tamaño pedido por esta
        # pestaña, y como el Notebook se agranda para la pestaña más grande,
        # terminaba agrandando TODA la ventana más allá de la pantalla. Con
        # esto, la tabla queda contenida en el espacio real disponible y las
        # columnas de más se ven moviendo la scrollbar horizontal (o con
        # Shift + rueda del mouse).
        frame_tabla = tk.Frame(contenedor, bg=COLOR_FONDO)
        frame_tabla.pack(side="top", fill="both", expand=True)
        frame_tabla.pack_propagate(False)

        claves = [c[0] for c in self.COLUMNAS_VECTOR]
        self.tree = ttk.Treeview(frame_tabla, columns=claves, show='headings', height=22)
        for clave, encabezado, ancho in self.COLUMNAS_VECTOR:
            self.tree.heading(clave, text=encabezado)
            self.tree.column(clave, width=ancho, anchor="center", stretch=False)

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        # Shift + rueda del mouse = scroll horizontal (más cómodo que ir a
        # buscar la barrita de abajo cuando hay tantas columnas).
        def _scroll_horizontal(event):
            self.tree.xview_scroll(int(-1 * (event.delta / 120)), "units")
        self.tree.bind("<Shift-MouseWheel>", _scroll_horizontal)

        self._filas_guardadas = []  # cache para "Ver Estado Gráfico"

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
            self.tree.insert('', 'end', values=self._valores_fila_para_tabla(fila))

    def _valores_fila_para_tabla(self, fila):
        """
        Arma la lista de valores de una fila para el Treeview, en el mismo
        orden que COLUMNAS_VECTOR. Las columnas fijas salen directo de la
        fila; las columnas "Visitante 1", "Visitante 2", ... se completan
        con el Estado y la Hora de llegada de cada visitante activo en ese
        instante (ordenados por ID). Si hay más visitantes activos que
        columnas disponibles, la última columna avisa "+N más" en vez de
        cortar la info sin explicación.
        """
        claves_fijas = [c[0] for c in self.COLUMNAS_VECTOR if not c[0].startswith('Vis')]
        valores = [fila.get(clave, '') for clave in claves_fijas]

        visitantes = sorted(fila.get('Visitantes_Activos_Detalle', []), key=lambda v: v['ID'])
        n = self.MAX_VISITANTES_MOSTRADOS
        for idx in range(n):
            if idx >= len(visitantes):
                valores.append('')
                valores.append('')
                continue

            if idx == n - 1 and len(visitantes) > n:
                restantes = len(visitantes) - idx
                valores.append(f"+{restantes} más")
                valores.append('')
            else:
                v = visitantes[idx]
                valores.append(v.get('Estado', ''))
                valores.append(v.get('Hora_Llegada', ''))

        return valores
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

    def abrir_visualizacion_grafica(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Atención", "Por favor, seleccioná una fila del Vector de Estado primero.")
            return
        idx = self.tree.index(seleccion[0])
        if idx >= len(self._filas_guardadas):
            return
        fila = self._filas_guardadas[idx]
        self._mostrar_ventana_grafica(fila)

    def _mostrar_ventana_grafica(self, fila):
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Visualización Gráfica — Iteración {fila['Iteracion']} (Día {fila['Dia']}, {fila['Hora_Aprox']})")
        ventana.geometry("1020x560")
        ventana.resizable(False, False)
        ventana.configure(bg="#F5F0E6")

        # Top label info
        info_str = f"Iteración: {fila['Iteracion']} | Día: {fila['Dia']} | Hora: {fila['Hora_Aprox']} | Evento: {fila['Evento']} | Reloj: {fila['Reloj_Global']} s"
        lbl_info = tk.Label(ventana, text=info_str, font=("Georgia", 11, "bold"), fg="#7A1F2B", bg="#F5F0E6", pady=8)
        lbl_info.pack(side="top", fill="x")

        # Canvas
        canvas = tk.Canvas(ventana, width=1000, height=490, bg="white", highlightthickness=0)
        canvas.pack(pady=(0, 10))

        # Enclosing border box (matches user drawing)
        canvas.create_rectangle(10, 30, 990, 480, outline="black", width=3)

        # Division vertical lines
        canvas.create_line(350, 30, 350, 480, fill="black", width=2)
        canvas.create_line(615, 30, 615, 480, fill="black", width=2)
        canvas.create_line(800, 30, 800, 480, fill="black", width=2)

        # Section headers (labels at top of sections)
        canvas.create_text(175, 18, text="folletos", font=("Segoe UI", 12, "bold"), fill="black")
        canvas.create_text(482, 18, text="pintura", font=("Segoe UI", 12, "bold"), fill="black")
        canvas.create_text(707, 18, text="stand cerveza", font=("Segoe UI", 12, "bold"), fill="black")
        canvas.create_text(900, 18, text="fotografía", font=("Segoe UI", 12, "bold"), fill="black")

        # Sub-header titles in folletos
        canvas.create_text(95, 38, text="ventanilla 1", font=("Segoe UI", 10, "bold"), fill="black")
        canvas.create_text(255, 38, text="ventanilla 2", font=("Segoe UI", 10, "bold"), fill="black")

        # Filter visitors by state/location
        visitantes = fila.get('Visitantes_Activos_Detalle', [])

        vis_v1_serv = [v for v in visitantes if v.get('Sala') == 'Ventanilla 1']
        vis_v1_cola = sorted([v for v in visitantes if v.get('Sala') == 'Cola Ventanilla 1'], key=lambda x: x['ID'])

        vis_v2_serv = [v for v in visitantes if v.get('Sala') == 'Ventanilla 2']
        vis_v2_cola = sorted([v for v in visitantes if v.get('Sala') == 'Cola Ventanilla 2'], key=lambda x: x['ID'])

        vis_pintura = sorted([v for v in visitantes if v.get('Sala') == 'Pintura'], key=lambda x: x['ID'])

        vis_cerv_serv = [v for v in visitantes if v.get('Estado') == 'Siendo atendido (cerveza)']
        vis_cerv_cola = sorted([v for v in visitantes if v.get('Estado') == 'En cola de cerveza' or v.get('Sala') == 'Cola Cerveza'], key=lambda x: x['ID'])
        vis_cerv_deg = sorted([v for v in visitantes if v.get('Estado') == 'Degustando cerveza'], key=lambda x: x['ID'])

        vis_foto = sorted([v for v in visitantes if v.get('Sala') == 'Fotografia' or v.get('Estado') == 'En Fotografia'], key=lambda x: x['ID'])

        # --- Draw employees ---
        def dibujar_empleado(x1, y1, x2, y2, name, is_occupied):
            canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black", width=2)
            canvas.create_text((x1+x2)/2, y1 + 18, text=name, font=("Segoe UI", 9, "bold"), fill="#2B2420")
            if not is_occupied:
                canvas.create_rectangle(x1+2, y2-22, x2-2, y2-2, fill="#A0D82D", outline="")
                canvas.create_text((x1+x2)/2, y2 - 12, text="libre", font=("Segoe UI", 9, "bold"), fill="black")
            else:
                canvas.create_text((x1+x2)/2, y2 - 12, text="Ocupado", font=("Segoe UI", 9, "bold"), fill="#C0392B")

        # Ventanilla 1 Employees
        dibujar_empleado(20, 52, 85, 122, "empleado1", len(vis_v1_serv) >= 1)
        dibujar_empleado(105, 52, 170, 122, "empleado2", len(vis_v1_serv) >= 2)

        # Ventanilla 2 Employees
        dibujar_empleado(180, 52, 245, 122, "empleado3", len(vis_v2_serv) >= 1)
        dibujar_empleado(265, 52, 330, 122, "empleado4", len(vis_v2_serv) >= 2)

        # Stand Cerveza Employees
        busy_cerv = len(vis_cerv_serv)
        cerv_libres_real = max(0, 2 - busy_cerv)
        dibujar_empleado(625, 52, 700, 122, "empleado\ncerveza 1", cerv_libres_real < 2)
        dibujar_empleado(710, 52, 785, 122, "empleado\ncerveza 2", cerv_libres_real < 1)

        # --- Draw visitor avatar helper ---
        def dibujar_avatar(x, y, label):
            # Circle bg
            canvas.create_oval(x-20, y-20, x+20, y+20, fill="#2E5B82", outline="")
            # Head
            canvas.create_oval(x-7, y-12, x+7, y+2, fill="#FFFFFF", outline="")
            # Shoulders/body
            canvas.create_arc(x-14, y-2, x+14, y+22, start=0, extent=180, fill="#FFFFFF", outline="")
            # Text label below
            canvas.create_text(x, y+32, text=label, font=("Segoe UI", 8, "bold"), fill="#2B2420")

        # --- Draw served visitors ---
        if len(vis_v1_serv) >= 1:
            dibujar_avatar(52, 165, f"vis. {vis_v1_serv[0]['ID']}")
        if len(vis_v1_serv) >= 2:
            dibujar_avatar(137, 165, f"vis. {vis_v1_serv[1]['ID']}")

        if len(vis_v2_serv) >= 1:
            dibujar_avatar(212, 165, f"vis. {vis_v2_serv[0]['ID']}")
        if len(vis_v2_serv) >= 2:
            dibujar_avatar(297, 165, f"vis. {vis_v2_serv[1]['ID']}")

        if len(vis_cerv_serv) >= 1:
            dibujar_avatar(662, 165, f"vis. {vis_cerv_serv[0]['ID']}")
        if len(vis_cerv_serv) >= 2:
            dibujar_avatar(747, 165, f"vis. {vis_cerv_serv[1]['ID']}")

        # --- Draw queues ---
        # Cola V1 Box
        canvas.create_rectangle(20, 220, 170, 450, outline="black", width=2)
        canvas.create_text(95, 232, text="cola v1", font=("Segoe UI", 9, "bold"), fill="black")
        for idx, v in enumerate(vis_v1_cola):
            y_pos = 270 + idx * 55
            if y_pos < 440:
                dibujar_avatar(95, y_pos, f"vis. {v['ID']}")
            else:
                canvas.create_text(95, 442, text=f"+ {len(vis_v1_cola) - idx} más", font=("Segoe UI", 8, "italic"), fill="black")
                break

        # Cola V2 Box
        canvas.create_rectangle(180, 220, 330, 450, outline="black", width=2)
        canvas.create_text(255, 232, text="cola v2", font=("Segoe UI", 9, "bold"), fill="black")
        for idx, v in enumerate(vis_v2_cola):
            y_pos = 270 + idx * 55
            if y_pos < 440:
                dibujar_avatar(255, y_pos, f"vis. {v['ID']}")
            else:
                canvas.create_text(255, 442, text=f"+ {len(vis_v2_cola) - idx} más", font=("Segoe UI", 8, "italic"), fill="black")
                break

        # Cola Cerveza Box
        canvas.create_rectangle(625, 220, 700, 450, outline="black", width=1)
        canvas.create_text(662, 232, text="cola v", font=("Segoe UI", 9, "bold"), fill="black")
        for idx, v in enumerate(vis_cerv_cola):
            y_pos = 270 + idx * 55
            if y_pos < 440:
                dibujar_avatar(662, y_pos, f"vis. {v['ID']}")
            else:
                canvas.create_text(662, 442, text=f"+{len(vis_cerv_cola)-idx}", font=("Segoe UI", 8, "italic"), fill="black")
                break

        # Bebiendo (degustando)
        canvas.create_rectangle(710, 220, 785, 450, outline="black", width=1)
        canvas.create_text(747, 232, text="bebiendo", font=("Segoe UI", 9, "bold"), fill="black")
        for idx, v in enumerate(vis_cerv_deg):
            y_pos = 270 + idx * 55
            if y_pos < 440:
                dibujar_avatar(747, y_pos, f"vis. {v['ID']}")
            else:
                canvas.create_text(747, 442, text=f"+{len(vis_cerv_deg)-idx}", font=("Segoe UI", 8, "italic"), fill="black")
                break

        # --- Draw Pintura Grid ---
        for idx, v in enumerate(vis_pintura):
            col = idx % 3
            row = idx // 3
            x_pos = 385 + col * 80
            y_pos = 100 + row * 85
            if y_pos < 450:
                dibujar_avatar(x_pos, y_pos, f"vis. {v['ID']}")
            else:
                canvas.create_text(482, 465, text=f"+ {len(vis_pintura) - idx} en Pintura", font=("Segoe UI", 9, "italic", "bold"), fill="#6D214F")
                break

        # --- Draw Fotografia Grid ---
        for idx, v in enumerate(vis_foto):
            col = idx % 2
            row = idx // 2
            x_pos = 850 + col * 90
            y_pos = 100 + row * 85
            if y_pos < 450:
                dibujar_avatar(x_pos, y_pos, f"vis. {v['ID']}")
            else:
                canvas.create_text(900, 465, text=f"+ {len(vis_foto) - idx} más", font=("Segoe UI", 9, "italic", "bold"), fill="#6D214F")
                break