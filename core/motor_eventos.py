import random
import math

from .visitante import Visitante
from .runge_kutta import calcular_tiempo_degustacion


class Simulador:
    """
    Motor de simulación por eventos discretos del Palacio Ferreyra.

    Cada jornada va de 9:00 a 22:00 hs (13 horas = 46800 segundos).
    Si se pide simular "varios días", se encadenan jornadas: al llegar
    a las 22 hs se reinician colas, salas y horarios de llegada, pero
    se acumulan las métricas y se sigue numerando iteraciones y
    visitantes en forma continua, para que el usuario vea el sistema
    funcionando día tras día.

    Todas las duraciones de sala (Pintura y Fotografía) usan
    distribución Normal (Box-Muller), tal como pide la cátedra.
    """

    SEGUNDOS_JORNADA = 13 * 3600  # 9 a 22 hs

    # Columnas "transitorias" del vector de estado: solo llevan valor en
    # la fila del evento donde se generaron; el resto de las filas quedan
    # en blanco, tal como en una planilla armada a mano.
    CAMPOS_EVENTO_VACIOS = [
        'RND1_LlegA', 'RND2_LlegA', 'TEntreLlegA',
        'RND1_LlegB', 'RND2_LlegB', 'TEntreLlegB',
        'RND1_LlegC', 'RND2_LlegC', 'TEntreLlegC',
        'RND_Informes', 'Informe', 'RND_EligeVent', 'Ventanilla',
        'RND_T_Foll', 'T_Foll', 'Fin_Foll',
        'RND_T_Pint', 'T_Pint', 'Fin_Pint',
        'RND_VaFoto', 'VaFoto',
        'RND_T_Foto', 'T_Foto', 'Fin_Foto',
        'RND_TomaBirra', 'TomaBirra',
        'RND_TpoServ', 'TpoServ',
        'RND_Edad', 'Edad', 'EsMayorEdad', 'TpoTomarRK',
        'Reg15Pint', 'Reg15Foto',
    ]

    def __init__(self, parametros):
        self.parametros = parametros

        self.reloj = 0.0          # reloj global (acumula todos los días simulados)
        self.reloj_dia = 0.0      # reloj relativo al día actual (0 a 46800)
        self.dia_actual = 1

        self.dias_a_simular = parametros.get('dias', 1)
        self.tiempo_x = parametros.get('tiempo_x', 0.0)
        self.paso_h = parametros.get('rk_h', 0.05)

        # La distribución de tiempos en salas es SIEMPRE Normal.
        self.dist_salas = "Normal"

        # Probabilidades del recorrido, todas parametrizables por el usuario
        self.prob_folletos = parametros.get('prob_folletos', 0.60)
        self.prob_fotografia = parametros.get('prob_fotografia', 0.40)
        self.prob_cerveza = parametros.get('prob_cerveza', 0.50)

        self.iteracion = 0
        self.visitantes_totales = 0
        self.vector_estado = []   # acá se guarda la "foto" de cada iteración pedida

        # --- Servidores (empleados) y colas ---
        # Cada ventanilla tiene 2 empleados. Cada slot es None (libre) o
        # {'visitante_id': int, 'fin': reloj_global} si está ocupado.
        self.ventanillas = {
            1: {'servidores': [None, None], 'cola': []},
            2: {'servidores': [None, None], 'cola': []},
        }

        # El stand de cerveza tiene 2 servidores, mismo esquema de slots.
        self.cerveza_servidores = [None, None]
        self.cola_cerveza = []

        # Visitantes activos en el sistema (no salieron todavía)
        self.visitantes_activos = {}
        # Guardamos a todos para poder graficar / depurar si hace falta
        self.visitantes_historicos = {}

        # --- Conteos en sala (para el control cada 15 min) ---
        self.personas_en_pintura = 0
        self.personas_en_fotografia = 0

        # --- MÉTRICAS OBLIGATORIAS ---
        self.acumulador_espera_v1 = 0.0
        self.visitantes_esperaron_v1 = 0
        self.acumulador_espera_v2 = 0.0
        self.visitantes_esperaron_v2 = 0
        self.acumulador_tiempo_permanencia = 0.0
        self.visitantes_finalizados = 0
        self.metricas_15_min = []

        # --- 5 MÉTRICAS EXTRA (todas distintas entre sí) ---
        self.metrica_total_folletos = 0                # 1) visitantes que pidieron folletos
        self.metrica_total_cervezas = 0                 # 2) cervezas servidas
        self.metrica_suma_edades_cerveza = 0.0           #    (auxiliar para promedio de edad)
        self.metrica_total_fotografia = 0                # 3) visitantes que entraron a fotografía
        self.metrica_abandonos_post_pintura = 0          # 4) personas que se van tras pintura (no van a foto)
        self.max_cola_cerveza = 0                      # 5) máxima longitud alcanzada por la cola de cerveza

        # Contador auxiliar para la columna "Cont Directo a Muestra"
        # (visitantes que van directo a Pintura sin pasar por folletos)
        self.metrica_directo_pintura = 0

        # Tablas de Runge-Kutta generadas, para mostrarlas en la interfaz
        self.tablas_rk_generadas = {}

        # Lista de eventos futuros: clave -> tiempo (en reloj GLOBAL, segundos)
        self.eventos = {}

        self._programar_llegadas_iniciales()
        self.eventos['Control_15min'] = self.reloj + (15 * 60)
        self.eventos['Fin_Jornada'] = self.reloj + self.SEGUNDOS_JORNADA

    # ------------------------------------------------------------------
    # Utilidades de números aleatorios (siempre devuelven también el rnd)
    # ------------------------------------------------------------------
    def generar_normal(self, media, desv):
        """Genera un valor con distribución Normal (Box-Muller) y devuelve
        también los dos números aleatorios [0,1) usados, truncando a un
        mínimo de 0.1 para asegurar tiempos siempre mayores que cero."""
        rnd1, rnd2 = random.random(), random.random()
        z = math.sqrt(-2 * math.log(rnd1)) * math.cos(2 * math.pi * rnd2)
        valor = max(0.1, media + desv * z)
        return valor, rnd1, rnd2

    def generar_uniforme(self, minimo, maximo):
        rnd = random.random()
        valor = minimo + rnd * (maximo - minimo)
        return valor, rnd

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------
    def _programar_llegadas_iniciales(self):
        media_a, desv_a = self.parametros['puerta_a']
        media_b, desv_b = self.parametros['puerta_b']
        media_c, desv_c = self.parametros['puerta_c']

        t_a, rnd1_a, rnd2_a = self.generar_normal(media_a, desv_a)
        t_b, rnd1_b, rnd2_b = self.generar_normal(media_b, desv_b)
        t_c, rnd1_c, rnd2_c = self.generar_normal(media_c, desv_c)

        self.eventos['Llegada_A'] = self.reloj + t_a
        # Puerta B arranca 2 hs después de abierto el palacio (11 hs)
        self.eventos['Llegada_B'] = self.reloj + 2 * 3600 + t_b
        # Puerta C arranca 3 hs después de la B (14 hs)
        self.eventos['Llegada_C'] = self.reloj + 5 * 3600 + t_c

    def _reiniciar_para_nuevo_dia(self):
        """Al llegar a las 22 hs, si quedan días por simular, arrancamos
        un nuevo día: se vacían colas y salas (el palacio cierra y al otro
        día vuelve a recibir gente desde cero), pero las métricas
        acumuladas NO se resetean."""
        self.dia_actual += 1
        self.reloj_dia = 0.0

        # Cerramos cualquier visitante que haya quedado "colgado" en el
        # sistema al cierre (no se cuenta su permanencia porque no llegó
        # a completar su recorrido en el horario de atención).
        self.visitantes_activos = {}
        self.personas_en_pintura = 0
        self.personas_en_fotografia = 0
        self.cerveza_servidores = [None, None]
        self.cola_cerveza = []
        self.ventanillas = {
            1: {'servidores': [None, None], 'cola': []},
            2: {'servidores': [None, None], 'cola': []},
        }

        # Limpiamos eventos pendientes del día anterior y reprogramamos
        # las llegadas del nuevo día
        self.eventos = {}
        self._programar_llegadas_iniciales()
        self.eventos['Control_15min'] = self.reloj + (15 * 60)
        self.eventos['Fin_Jornada'] = self.reloj + self.SEGUNDOS_JORNADA

    # ------------------------------------------------------------------
    # Tiempos de sala según la tabla del enunciado (dependen de la hora)
    # Siempre Normal, como pide la cátedra.
    # ------------------------------------------------------------------
    def determinar_tiempo_sala(self, sala):
        hora_actual = 9 + (self.reloj_dia / 3600)

        tiempos = self.parametros['salas'][sala]
        if 9 <= hora_actual < 12: media, desv = tiempos['9_12']
        elif 12 <= hora_actual < 14: media, desv = tiempos['12_14']
        elif 14 <= hora_actual < 18: media, desv = tiempos['14_18']
        else: media, desv = tiempos['18_22']

        return self.generar_normal(media, desv)

    # ------------------------------------------------------------------
    # Helpers de slots de servidores (empleados)
    # ------------------------------------------------------------------
    def _slot_libre_ventanilla(self, v):
        for i, s in enumerate(self.ventanillas[v]['servidores']):
            if s is None:
                return i
        return None

    def _slot_libre_cerveza(self):
        for i, s in enumerate(self.cerveza_servidores):
            if s is None:
                return i
        return None

    def _estado_slot(self, slot):
        if slot is None:
            return "Libre"
        return f"Ocupado (Vis.{slot['visitante_id']})"

    def _fin_slot(self, slot):
        if slot is None:
            return ""
        return self.formatear_hora_reloj(slot['fin'])

    # ------------------------------------------------------------------
    # Snapshot de TODO el sistema en el instante actual
    # ------------------------------------------------------------------
    def _campos_evento_vacios(self):
        return {campo: "" for campo in self.CAMPOS_EVENTO_VACIOS}

    def _snapshot_sistema(self, evento_actual, campos_evento=None):
        """
        Construye la fila del vector de estado tipo planilla: una fila por
        evento, con columnas transitorias (RNDs y resultados generados
        justo en ESE evento, en blanco en el resto de las filas) más
        columnas de estado permanente (colas, servidores, acumuladores),
        que siempre reflejan la foto actual del sistema.
        """
        if campos_evento is None:
            campos_evento = {}

        fila = self._campos_evento_vacios()
        fila.update(campos_evento)

        v1 = self.ventanillas[1]['servidores']
        v2 = self.ventanillas[2]['servidores']
        c = self.cerveza_servidores

        fila.update({
            'Iteracion': self.iteracion,
            'Dia': self.dia_actual,
            'Reloj_Global': round(self.reloj, 2),
            'Reloj_Dia': round(self.reloj_dia, 2),
            'Hora_Aprox': self._formatear_hora(),
            'Evento': evento_actual,

            'ProxLlegA': round(self.eventos.get('Llegada_A', 0), 2),
            'ProxLlegB': round(self.eventos.get('Llegada_B', 0), 2),
            'ProxLlegC': round(self.eventos.get('Llegada_C', 0), 2),

            'ColaV1': len(self.ventanillas[1]['cola']),
            'ColaV2': len(self.ventanillas[2]['cola']),
            'V1E1_Estado': self._estado_slot(v1[0]), 'V1E1_Fin': self._fin_slot(v1[0]),
            'V1E2_Estado': self._estado_slot(v1[1]), 'V1E2_Fin': self._fin_slot(v1[1]),
            'V2E1_Estado': self._estado_slot(v2[0]), 'V2E1_Fin': self._fin_slot(v2[0]),
            'V2E2_Estado': self._estado_slot(v2[1]), 'V2E2_Fin': self._fin_slot(v2[1]),

            'PersPintura': self.personas_en_pintura,
            'PersFoto': self.personas_en_fotografia,

            'ColaStand': len(self.cola_cerveza),
            'CervE1_Estado': self._estado_slot(c[0]), 'CervE1_Fin': self._fin_slot(c[0]),
            'CervE2_Estado': self._estado_slot(c[1]), 'CervE2_Fin': self._fin_slot(c[1]),

            'ProxControl15': self.formatear_hora_reloj(self.eventos.get('Control_15min')) if 'Control_15min' in self.eventos else "",

            'AC_EsperaV1': round(self.acumulador_espera_v1, 2),
            'ContClientesV1': self.visitantes_esperaron_v1,
            'AC_EsperaV2': round(self.acumulador_espera_v2, 2),
            'ContClientesV2': self.visitantes_esperaron_v2,
            'AC_Permanencia': round(self.acumulador_tiempo_permanencia, 2),
            'ContSalen': self.visitantes_finalizados,
            'ContBirras': self.metrica_total_cervezas,
            'AC_Edades': round(self.metrica_suma_edades_cerveza, 2),
            'ContDirecto': self.metrica_directo_pintura,

            'Visitantes_Activos_Detalle': [vis.snapshot(self) for vis in self.visitantes_activos.values()],
            'Cantidad_Visitantes_Activos': len(self.visitantes_activos),
        })
        return fila

    def _formatear_hora(self):
        total_seg = self.reloj_dia
        horas = int(9 + total_seg // 3600)
        minutos = int((total_seg % 3600) // 60)
        segundos = int(total_seg % 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    def formatear_hora_reloj(self, T):
        if T is None:
            return ""
        relative_seg = T - self.reloj + self.reloj_dia
        horas = int(9 + relative_seg // 3600)
        minutos = int((relative_seg % 3600) // 60)
        segundos = int(relative_seg % 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    # ------------------------------------------------------------------
    # Bucle principal de simulación
    # ------------------------------------------------------------------
    def simular(self, iteraciones_max, desde_j, cantidad_i):
        while self.iteracion < iteraciones_max:

            evento_actual, tiempo_evento = min(self.eventos.items(), key=lambda x: x[1])
            # --- CORTE POR TIEMPO X ---
            if self.tiempo_x > 0 and tiempo_evento > self.tiempo_x:
                fila_final = self._snapshot_sistema("Fin por Instante X")
                fila_final['Visitantes_Activos_Detalle'] = []  # Sin temporales
                self.vector_estado.append(fila_final)
                break
            avance = tiempo_evento - self.reloj
            self.reloj = tiempo_evento
            self.reloj_dia += avance

            campos = {}

            # --- FIN DE JORNADA (22 hs) ---
            if evento_actual == 'Fin_Jornada':
                # Guardamos la fila final del día (sin objetos temporales,
                # tal como pide la consigna para la fila del instante X)
                fila_final = self._snapshot_sistema(evento_actual)
                fila_final['Visitantes_Activos_Detalle'] = []  # sin temporales
                self.vector_estado.append(fila_final)

                if self.dia_actual >= self.dias_a_simular:
                    break
                else:
                    self._reiniciar_para_nuevo_dia()
                    self.iteracion += 1
                    continue

            # --- LLEGADAS (PUERTAS A, B, C) ---
            elif evento_actual in ('Llegada_A', 'Llegada_B', 'Llegada_C'):
                puerta = evento_actual[-1]
                clave_param = {'A': 'puerta_a', 'B': 'puerta_b', 'C': 'puerta_c'}[puerta]
                media, desv = self.parametros[clave_param]
                t_next, rnd1, rnd2 = self.generar_normal(media, desv)
                campos[f'RND1_Lleg{puerta}'] = round(rnd1, 4)
                campos[f'RND2_Lleg{puerta}'] = round(rnd2, 4)
                campos[f'TEntreLleg{puerta}'] = round(t_next, 2)
                self.eventos[evento_actual] = self.reloj + t_next

                self.visitantes_totales += 1
                media_edad = self.parametros.get('edad_media', 30)
                nuevo = Visitante(self.visitantes_totales, self.reloj, puerta, media_edad)
                self.visitantes_activos[nuevo.id] = nuevo
                self.visitantes_historicos[nuevo.id] = nuevo
                campos['RND_Edad'] = round(nuevo.rnd_edad, 4)
                campos['Edad'] = nuevo.edad
                campos['EsMayorEdad'] = "SI" if nuevo.edad >= 18 else "NO"

                rnd_decision = random.random()
                nuevo.rnd_decision_folletos = rnd_decision
                campos['RND_Informes'] = round(rnd_decision, 4)

                if rnd_decision <= self.prob_folletos:
                    nuevo.fue_a_folletos = True
                    campos['Informe'] = "SI"
                    rnd_vent = random.random()
                    nuevo.rnd_ventanilla_elegida = rnd_vent
                    v_elegida = 1 if rnd_vent < 0.5 else 2
                    nuevo.ventanilla = v_elegida
                    campos['RND_EligeVent'] = round(rnd_vent, 4)
                    campos['Ventanilla'] = v_elegida

                    slot_idx = self._slot_libre_ventanilla(v_elegida)
                    if slot_idx is not None:
                        media_f, desv_f = self.parametros['folletos']
                        t_folletos, rnd_f = self.generar_uniforme(media_f - desv_f, media_f + desv_f)
                        fin = self.reloj + t_folletos
                        self.ventanillas[v_elegida]['servidores'][slot_idx] = {'visitante_id': nuevo.id, 'fin': fin}
                        nuevo.rnd_tiempo_folletos = rnd_f
                        nuevo.duracion_folletos = t_folletos
                        nuevo.fin_folletos_reloj = fin
                        nuevo.estado = "En ventanilla"
                        nuevo.sala_actual = f"Ventanilla {v_elegida}"
                        nuevo.destino = "Pintura"
                        self.eventos[f'Fin_Folletos_{v_elegida}_{slot_idx}_{nuevo.id}'] = fin
                        self.metrica_total_folletos += 1
                        campos['RND_T_Foll'] = round(rnd_f, 4)
                        campos['T_Foll'] = round(t_folletos, 2)
                        campos['Fin_Foll'] = self.formatear_hora_reloj(fin)
                    else:
                        nuevo.inicio_cola_informes = self.reloj
                        nuevo.estado = "En cola de informes"
                        nuevo.sala_actual = f"Cola Ventanilla {v_elegida}"
                        nuevo.destino = f"Ventanilla {v_elegida}"
                        self.ventanillas[v_elegida]['cola'].append(nuevo)
                else:
                    nuevo.fue_a_folletos = False
                    campos['Informe'] = "NO"
                    self.metrica_directo_pintura += 1
                    nuevo.estado = "En Pintura"
                    nuevo.sala_actual = "Pintura"
                    nuevo.destino = "Por decidir"
                    nuevo.inicio_pintura = self.reloj
                    t_pintura, rnd_p1, rnd_p2 = self.determinar_tiempo_sala("Pintura")
                    nuevo.rnd_tiempo_pintura = (rnd_p1, rnd_p2)
                    nuevo.duracion_pintura = t_pintura
                    fin_pint = self.reloj + t_pintura
                    nuevo.fin_pintura_reloj = fin_pint
                    self.eventos[f'Fin_Pintura_{nuevo.id}'] = fin_pint
                    self.personas_en_pintura += 1
                    campos['RND_T_Pint'] = f"{rnd_p1:.4f}, {rnd_p2:.4f}"
                    campos['T_Pint'] = round(t_pintura, 2)
                    campos['Fin_Pint'] = self.formatear_hora_reloj(fin_pint)

            # --- SALIDA DE FOLLETOS ---
            elif evento_actual.startswith('Fin_Folletos_'):
                partes = evento_actual.split('_')
                v_id = int(partes[2])
                slot_idx = int(partes[3])
                id_vis = int(partes[-1])
                visitante = self.visitantes_activos[id_vis]

                self.ventanillas[v_id]['servidores'][slot_idx] = None  # libera el slot

                visitante.fin_cola_informes = self.reloj
                visitante.estado = "En Pintura"
                visitante.sala_actual = "Pintura"
                visitante.destino = "Por decidir"
                visitante.inicio_pintura = self.reloj
                t_pintura, rnd_p1, rnd_p2 = self.determinar_tiempo_sala("Pintura")
                visitante.rnd_tiempo_pintura = (rnd_p1, rnd_p2)
                visitante.duracion_pintura = t_pintura
                fin_pint = self.reloj + t_pintura
                visitante.fin_pintura_reloj = fin_pint
                self.eventos[f'Fin_Pintura_{visitante.id}'] = fin_pint
                self.personas_en_pintura += 1
                campos['RND_T_Pint'] = f"{rnd_p1:.4f}, {rnd_p2:.4f}"
                campos['T_Pint'] = round(t_pintura, 2)
                campos['Fin_Pint'] = self.formatear_hora_reloj(fin_pint)

                if len(self.ventanillas[v_id]['cola']) > 0:
                    siguiente = self.ventanillas[v_id]['cola'].pop(0)

                    tiempo_esperado = self.reloj - siguiente.inicio_cola_informes
                    if v_id == 1:
                        self.acumulador_espera_v1 += tiempo_esperado
                        self.visitantes_esperaron_v1 += 1
                    else:
                        self.acumulador_espera_v2 += tiempo_esperado
                        self.visitantes_esperaron_v2 += 1

                    siguiente.estado = "En ventanilla"
                    siguiente.sala_actual = f"Ventanilla {v_id}"
                    siguiente.destino = "Pintura"
                    media_f, desv_f = self.parametros['folletos']
                    t_folletos, rnd_f = self.generar_uniforme(media_f - desv_f, media_f + desv_f)
                    fin = self.reloj + t_folletos
                    self.ventanillas[v_id]['servidores'][slot_idx] = {'visitante_id': siguiente.id, 'fin': fin}
                    siguiente.rnd_tiempo_folletos = rnd_f
                    siguiente.duracion_folletos = t_folletos
                    siguiente.fin_folletos_reloj = fin
                    self.eventos[f'Fin_Folletos_{v_id}_{slot_idx}_{siguiente.id}'] = fin
                    self.metrica_total_folletos += 1
                    campos['RND_T_Foll'] = round(rnd_f, 4)
                    campos['T_Foll'] = round(t_folletos, 2)
                    campos['Fin_Foll'] = self.formatear_hora_reloj(fin)

            # --- SALIDA DE PINTURA ---
            elif evento_actual.startswith('Fin_Pintura_'):
                id_vis = int(evento_actual.split('_')[-1])
                visitante = self.visitantes_activos[id_vis]
                visitante.fin_pintura = self.reloj
                self.personas_en_pintura -= 1

                rnd_foto = random.random()
                visitante.rnd_decision_fotografia = rnd_foto
                campos['RND_VaFoto'] = round(rnd_foto, 4)

                if rnd_foto <= self.prob_fotografia:
                    visitante.fue_a_fotografia = True
                    campos['VaFoto'] = "SI"
                    self.metrica_total_fotografia += 1
                    self.personas_en_fotografia += 1

                    # --- Regla de negocio: los menores de 18 no pueden
                    # degustar cerveza. Directamente no se sortea la
                    # decisión (no tiene sentido tirar el dado si la
                    # respuesta está prohibida de antemano), y queda
                    # marcado con un motivo claro en vez de un simple "NO".
                    if visitante.edad < 18:
                        decide_tomar = False
                        campos['TomaBirra'] = "No, menor de edad"
                    else:
                        rnd_cerveza = random.random()
                        visitante.rnd_decision_cerveza = rnd_cerveza
                        campos['RND_TomaBirra'] = round(rnd_cerveza, 4)
                        decide_tomar = rnd_cerveza <= self.prob_cerveza
                        campos['TomaBirra'] = "SI" if decide_tomar else "NO"

                    if decide_tomar:
                        visitante.tomo_cerveza = True
                        slot_idx = self._slot_libre_cerveza()
                        if slot_idx is not None:
                            min_c, max_c = self.parametros['cerveza']
                            t_servicio, rnd_s = self.generar_uniforme(min_c, max_c)
                            fin = self.reloj + t_servicio
                            self.cerveza_servidores[slot_idx] = {'visitante_id': visitante.id, 'fin': fin}
                            visitante.rnd_tiempo_cerveza = rnd_s
                            visitante.duracion_cerveza = t_servicio
                            visitante.fin_cerveza_reloj = fin
                            visitante.estado = "Siendo atendido (cerveza)"
                            visitante.sala_actual = "Stand Cerveza"
                            visitante.destino = "Degustación Cerveza"
                            visitante.inicio_cerveza = self.reloj
                            self.eventos[f'Fin_Servicio_Cerveza_{slot_idx}_{visitante.id}'] = fin
                            campos['RND_TpoServ'] = round(rnd_s, 4)
                            campos['TpoServ'] = round(t_servicio, 2)
                        else:
                            visitante.inicio_cola_cerveza = self.reloj
                            visitante.estado = "En cola de cerveza"
                            visitante.sala_actual = "Cola Cerveza"
                            visitante.destino = "Stand Cerveza"
                            self.cola_cerveza.append(visitante)
                            self.max_cola_cerveza = max(self.max_cola_cerveza, len(self.cola_cerveza))

                    else:
                        visitante.tomo_cerveza = False
                        visitante.estado = "En Fotografia"
                        visitante.sala_actual = "Fotografia"
                        visitante.destino = "Salida"
                        visitante.inicio_fotografia = self.reloj
                        t_foto, rnd_foto1, rnd_foto2 = self.determinar_tiempo_sala("Fotografia")
                        visitante.rnd_tiempo_fotografia = (rnd_foto1, rnd_foto2)
                        visitante.duracion_fotografia = t_foto
                        fin_foto = self.reloj + t_foto
                        visitante.fin_fotografia_reloj = fin_foto
                        self.eventos[f'Fin_Fotografia_{visitante.id}'] = fin_foto
                        campos['RND_T_Foto'] = f"{rnd_foto1:.4f}, {rnd_foto2:.4f}"
                        campos['T_Foto'] = round(t_foto, 2)
                        campos['Fin_Foto'] = self.formatear_hora_reloj(fin_foto)
                else:
                    # Se va del sistema directamente tras pintura
                    visitante.fue_a_fotografia = False
                    campos['VaFoto'] = "NO"
                    visitante.estado = "Salio"
                    visitante.sala_actual = "Fuera"
                    visitante.destino = "Salida"
                    visitante.reloj_salida = self.reloj
                    self.metrica_abandonos_post_pintura += 1

                    tiempo_permanencia = self.reloj - visitante.reloj_llegada
                    self.acumulador_tiempo_permanencia += tiempo_permanencia
                    self.visitantes_finalizados += 1

                    del self.visitantes_activos[visitante.id]

            # --- LE ENTREGAN LA CERVEZA (empieza la degustación) ---
            elif evento_actual.startswith('Fin_Servicio_Cerveza_'):
                partes = evento_actual.split('_')
                slot_idx = int(partes[3])
                id_vis = int(partes[-1])
                visitante = self.visitantes_activos[id_vis]
                visitante.fin_cerveza = self.reloj
                self.metrica_total_cervezas += 1
                self.metrica_suma_edades_cerveza += visitante.edad

                self.cerveza_servidores[slot_idx] = None  # libera el slot

                if len(self.cola_cerveza) > 0:
                    siguiente = self.cola_cerveza.pop(0)
                    min_c, max_c = self.parametros['cerveza']
                    t_servicio, rnd_s = self.generar_uniforme(min_c, max_c)
                    fin = self.reloj + t_servicio
                    self.cerveza_servidores[slot_idx] = {'visitante_id': siguiente.id, 'fin': fin}
                    siguiente.rnd_tiempo_cerveza = rnd_s
                    siguiente.duracion_cerveza = t_servicio
                    siguiente.fin_cerveza_reloj = fin
                    siguiente.estado = "Siendo atendido (cerveza)"
                    siguiente.sala_actual = "Stand Cerveza"
                    siguiente.destino = "Degustación Cerveza"
                    siguiente.inicio_cerveza = self.reloj
                    self.eventos[f'Fin_Servicio_Cerveza_{slot_idx}_{siguiente.id}'] = fin
                    campos['RND_TpoServ'] = round(rnd_s, 4)
                    campos['TpoServ'] = round(t_servicio, 2)

                tiempo_degustacion, tabla_rk = calcular_tiempo_degustacion(visitante.edad, self.paso_h)
                self.tablas_rk_generadas[
                    f"Visitante {visitante.id} (Edad: {visitante.edad}, Dia {self.dia_actual})"
                ] = tabla_rk
                campos['TpoTomarRK'] = round(tiempo_degustacion, 2)

                visitante.estado = "Degustando cerveza"
                visitante.sala_actual = "Stand Cerveza"
                visitante.destino = "Fotografía"
                visitante.inicio_degustacion = self.reloj
                self.eventos[f'Fin_Degustacion_{visitante.id}'] = self.reloj + tiempo_degustacion

            # --- TERMINA DE BEBER ---
            elif evento_actual.startswith('Fin_Degustacion_'):
                id_vis = int(evento_actual.split('_')[-1])
                visitante = self.visitantes_activos[id_vis]
                visitante.fin_degustacion = self.reloj

                visitante.estado = "En Fotografia"
                visitante.sala_actual = "Fotografia"
                visitante.destino = "Salida"
                visitante.inicio_fotografia = self.reloj
                t_foto, rnd_foto1, rnd_foto2 = self.determinar_tiempo_sala("Fotografia")
                visitante.rnd_tiempo_fotografia = (rnd_foto1, rnd_foto2)
                visitante.duracion_fotografia = t_foto
                fin_foto = self.reloj + t_foto
                visitante.fin_fotografia_reloj = fin_foto
                self.eventos[f'Fin_Fotografia_{visitante.id}'] = fin_foto
                campos['RND_T_Foto'] = f"{rnd_foto1:.4f}, {rnd_foto2:.4f}"
                campos['T_Foto'] = round(t_foto, 2)
                campos['Fin_Foto'] = self.formatear_hora_reloj(fin_foto)

            # --- FIN DE RECORRIDO (sale de fotografía) ---
            elif evento_actual.startswith('Fin_Fotografia_'):
                id_vis = int(evento_actual.split('_')[-1])
                visitante = self.visitantes_activos[id_vis]
                visitante.fin_fotografia = self.reloj
                visitante.estado = "Salio"
                visitante.sala_actual = "Fuera"
                visitante.destino = "Salida"
                visitante.reloj_salida = self.reloj
                self.personas_en_fotografia -= 1

                tiempo_permanencia = self.reloj - visitante.reloj_llegada
                self.acumulador_tiempo_permanencia += tiempo_permanencia
                self.visitantes_finalizados += 1

                del self.visitantes_activos[visitante.id]

            # --- CONTROL CADA 15 MINUTOS ---
            elif evento_actual == 'Control_15min':
                self.eventos['Control_15min'] = self.reloj + (15 * 60)
                campos['Reg15Pint'] = self.personas_en_pintura
                campos['Reg15Foto'] = self.personas_en_fotografia
                self.metricas_15_min.append({
                    'Dia': self.dia_actual,
                    'Hora': self._formatear_hora(),
                    'Reloj_Global': round(self.reloj, 2),
                    'En_Pintura': self.personas_en_pintura,
                    'En_Fotografia': self.personas_en_fotografia,
                })

            # Limpieza de eventos puntuales ya disparados (los recurrentes
            # ya fueron reprogramados arriba con la misma clave)
            eventos_recurrentes = ('Llegada_A', 'Llegada_B', 'Llegada_C', 'Control_15min', 'Fin_Jornada')
            if evento_actual not in eventos_recurrentes and evento_actual in self.eventos:
                del self.eventos[evento_actual]

            # --- GUARDADO DE LA FILA EN EL VECTOR DE ESTADO ---
            fila = self._snapshot_sistema(evento_actual, campos)
            self.vector_estado.append(fila)

            self.iteracion += 1

        return self.vector_estado

    # ------------------------------------------------------------------
    # Resumen de métricas, listo para mostrar en la interfaz
    # ------------------------------------------------------------------
    def obtener_metricas(self):
        prom_permanencia = (
            self.acumulador_tiempo_permanencia / self.visitantes_finalizados
            if self.visitantes_finalizados > 0 else 0.0
        )
        prom_cola_v1 = (
            self.acumulador_espera_v1 / self.visitantes_esperaron_v1
            if self.visitantes_esperaron_v1 > 0 else 0.0
        )
        prom_cola_v2 = (
            self.acumulador_espera_v2 / self.visitantes_esperaron_v2
            if self.visitantes_esperaron_v2 > 0 else 0.0
        )
        prom_edad_cerveza = (
            self.metrica_suma_edades_cerveza / self.metrica_total_cervezas
            if self.metrica_total_cervezas > 0 else 0.0
        )

        return {
            'prom_permanencia': prom_permanencia,
            'prom_cola_v1': prom_cola_v1,
            'prom_cola_v2': prom_cola_v2,
            'visitantes_totales': self.visitantes_totales,
            'visitantes_finalizados': self.visitantes_finalizados,
            'total_folletos': self.metrica_total_folletos,
            'total_cervezas': self.metrica_total_cervezas,
            'prom_edad_cerveza': prom_edad_cerveza,
            'total_fotografia': self.metrica_total_fotografia,
            'abandonos_post_pintura': self.metrica_abandonos_post_pintura,
            'max_cola_cerveza': self.max_cola_cerveza,
        }