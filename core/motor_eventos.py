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
    """

    SEGUNDOS_JORNADA = 13 * 3600  # 9 a 22 hs

    def __init__(self, parametros):
        self.parametros = parametros

        self.reloj = 0.0          # reloj global (acumula todos los días simulados)
        self.reloj_dia = 0.0      # reloj relativo al día actual (0 a 46800)
        self.dia_actual = 1

        self.dias_a_simular = parametros.get('dias', 1)
        self.dias_a_simular = parametros.get('dias', 1)
        self.tiempo_x = parametros.get('tiempo_x', 0.0)
        self.paso_h = parametros.get('rk_h', 0.05)
        self.dist_salas = parametros.get('dist_salas', 'Normal')

        # Probabilidades del recorrido, todas parametrizables por el usuario
        self.prob_folletos = parametros.get('prob_folletos', 0.60)
        self.prob_fotografia = parametros.get('prob_fotografia', 0.40)
        self.prob_cerveza = parametros.get('prob_cerveza', 0.50)

        self.iteracion = 0
        self.visitantes_totales = 0
        self.vector_estado = []   # acá se guarda la "foto" de cada iteración pedida

        # --- Servidores y colas ---
        self.servidores_cerveza = 2
        self.cola_cerveza = []

        self.ventanillas = {
            1: {'libres': 2, 'cola': []},
            2: {'libres': 2, 'cola': []},
        }

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

        # Almacenamiento de RNDs de próximas llegadas
        self.prox_llegadas_rnd = {'A': "", 'B': "", 'C': ""}

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

        self.prox_llegadas_rnd['A'] = f"{rnd1_a:.4f}, {rnd2_a:.4f}"
        self.prox_llegadas_rnd['B'] = f"{rnd1_b:.4f}, {rnd2_b:.4f}"
        self.prox_llegadas_rnd['C'] = f"{rnd1_c:.4f}, {rnd2_c:.4f}"

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
        self.servidores_cerveza = 2
        self.cola_cerveza = []
        self.ventanillas = {
            1: {'libres': 2, 'cola': []},
            2: {'libres': 2, 'cola': []},
        }

        # Limpiamos eventos pendientes del día anterior y reprogramamos
        # las llegadas del nuevo día
        self.eventos = {}
        self._programar_llegadas_iniciales()
        self.eventos['Control_15min'] = self.reloj + (15 * 60)
        self.eventos['Fin_Jornada'] = self.reloj + self.SEGUNDOS_JORNADA

    # ------------------------------------------------------------------
    # Tiempos de sala según la tabla del enunciado (dependen de la hora)
    # ------------------------------------------------------------------
    def determinar_tiempo_sala(self, sala):
        hora_actual = 9 + (self.reloj_dia / 3600)
        
        # Mapeo de medias y desvíos/tolerancias según la hora (desde los parámetros)
        tiempos = self.parametros['salas'][sala]
        if 9 <= hora_actual < 12: media, desv = tiempos['9_12']
        elif 12 <= hora_actual < 14: media, desv = tiempos['12_14']
        elif 14 <= hora_actual < 18: media, desv = tiempos['14_18']
        else: media, desv = tiempos['18_22']

        if self.dist_salas == "Uniforme":

            tiempo, rnd = self.generar_uniforme(media - desv, media + desv)
            return tiempo, rnd, None
        else:
           
            return self.generar_normal(media, desv)

    # ------------------------------------------------------------------
    # Snapshot de TODO el sistema en el instante actual
    # ------------------------------------------------------------------
    def _snapshot_sistema(self, evento_actual):
        """
        Construye la fila del vector de estado: datos generales +
        una lista con el detalle de cada visitante activo en ese instante
        (solo los que siguen en el sistema, como pide la consigna).
        """
        visitantes_snapshot = []
        for vis in self.visitantes_activos.values():
            visitantes_snapshot.append(vis.snapshot())

        return {
            'Iteracion': self.iteracion,
            'Dia': self.dia_actual,
            'Reloj_Global': round(self.reloj, 2),
            'Reloj_Dia': round(self.reloj_dia, 2),
            'Hora_Aprox': self._formatear_hora(),
            'Evento': evento_actual,
            'En_Cola_Informes_V1': len(self.ventanillas[1]['cola']),
            'En_Cola_Informes_V2': len(self.ventanillas[2]['cola']),
            'En_Pintura': self.personas_en_pintura,
            'En_Cola_Cerveza': len(self.cola_cerveza),
            'Servidores_Cerveza_Libres': self.servidores_cerveza,
            'En_Fotografia': self.personas_en_fotografia,
            'Prox_Lleg_A': round(self.eventos.get('Llegada_A', 0), 2),
            'RND_Lleg_A': self.prox_llegadas_rnd.get('A', ''),
            'Prox_Lleg_B': round(self.eventos.get('Llegada_B', 0), 2),
            'RND_Lleg_B': self.prox_llegadas_rnd.get('B', ''),
            'Prox_Lleg_C': round(self.eventos.get('Llegada_C', 0), 2),
            'RND_Lleg_C': self.prox_llegadas_rnd.get('C', ''),
            'Visitantes_Activos_Detalle': visitantes_snapshot,
            'Cantidad_Visitantes_Activos': len(visitantes_snapshot),
        }

    def _formatear_hora(self):
        total_seg = self.reloj_dia
        horas = int(9 + total_seg // 3600)
        minutos = int((total_seg % 3600) // 60)
        segundos = int(total_seg % 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    # ------------------------------------------------------------------
    # Bucle principal de simulación
    # ------------------------------------------------------------------
    def simular(self, iteraciones_max, desde_j, cantidad_i):
        ultima_fila_guardada = False

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

            # --- FIN DE JORNADA (22 hs) ---
            if evento_actual == 'Fin_Jornada':
                # Guardamos la fila final del día (sin objetos temporales,
                # tal como pide la consigna para la fila del instante X)
                fila_final = self._snapshot_sistema(evento_actual)
                fila_final['Visitantes_Activos_Detalle'] = []  # sin temporales
                self.vector_estado.append(fila_final)

                if self.dia_actual >= self.dias_a_simular:
                    ultima_fila_guardada = True
                    break
                else:
                    self._reiniciar_para_nuevo_dia()
                    self.iteracion += 1
                    continue

            # --- LLEGADAS (PUERTAS A, B, C) ---
            if evento_actual in ('Llegada_A', 'Llegada_B', 'Llegada_C'):
                puerta = evento_actual[-1]
                clave_param = {'A': 'puerta_a', 'B': 'puerta_b', 'C': 'puerta_c'}[puerta]
                media, desv = self.parametros[clave_param]
                t_next, rnd1, rnd2 = self.generar_normal(media, desv)
                self.prox_llegadas_rnd[puerta] = f"{rnd1:.4f}, {rnd2:.4f}"
                self.eventos[evento_actual] = self.reloj + t_next

                self.visitantes_totales += 1
                media_edad = self.parametros.get('edad_media', 30)
                nuevo = Visitante(self.visitantes_totales, self.reloj, puerta, media_edad)
                self.visitantes_activos[nuevo.id] = nuevo
                self.visitantes_historicos[nuevo.id] = nuevo

                rnd_decision = random.random()
                nuevo.rnd_decision_folletos = rnd_decision

                if rnd_decision <= self.prob_folletos:
                    nuevo.fue_a_folletos = True
                    rnd_vent = random.random()
                    nuevo.rnd_ventanilla_elegida = rnd_vent
                    v_elegida = 1 if rnd_vent < 0.5 else 2
                    nuevo.ventanilla = v_elegida

                    if self.ventanillas[v_elegida]['libres'] > 0:
                        self.ventanillas[v_elegida]['libres'] -= 1
                        media_f, desv_f = self.parametros['folletos']
                        t_folletos, rnd_f = self.generar_uniforme(media_f - desv_f, media_f + desv_f)
                        nuevo.rnd_tiempo_folletos = rnd_f
                        nuevo.estado = "En ventanilla"
                        nuevo.sala_actual = f"Ventanilla {v_elegida}"
                        self.eventos[f'Fin_Folletos_{v_elegida}_{nuevo.id}'] = self.reloj + t_folletos
                        self.metrica_total_folletos += 1
                    else:
                        nuevo.inicio_cola_informes = self.reloj
                        nuevo.estado = "En cola de informes"
                        nuevo.sala_actual = f"Cola Ventanilla {v_elegida}"
                        self.ventanillas[v_elegida]['cola'].append(nuevo)
                else:
                    nuevo.fue_a_folletos = False
                    nuevo.estado = "En Pintura"
                    nuevo.sala_actual = "Pintura"
                    nuevo.inicio_pintura = self.reloj
                    t_pintura, rnd_p1, rnd_p2 = self.determinar_tiempo_sala("Pintura")
                    nuevo.rnd_tiempo_pintura = (rnd_p1, rnd_p2)
                    self.eventos[f'Fin_Pintura_{nuevo.id}'] = self.reloj + t_pintura
                    self.personas_en_pintura += 1

            # --- SALIDA DE FOLLETOS ---
            elif evento_actual.startswith('Fin_Folletos_'):
                partes = evento_actual.split('_')
                v_id = int(partes[2])
                id_vis = int(partes[-1])
                visitante = self.visitantes_activos[id_vis]

                visitante.fin_cola_informes = self.reloj
                visitante.estado = "En Pintura"
                visitante.sala_actual = "Pintura"
                visitante.inicio_pintura = self.reloj
                t_pintura, rnd_p1, rnd_p2 = self.determinar_tiempo_sala("Pintura")
                visitante.rnd_tiempo_pintura = (rnd_p1, rnd_p2)
                self.eventos[f'Fin_Pintura_{visitante.id}'] = self.reloj + t_pintura
                self.personas_en_pintura += 1

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
                    media_f, desv_f = self.parametros['folletos']
                    t_folletos, rnd_f = self.generar_uniforme(media_f - desv_f, media_f + desv_f)
                    siguiente.rnd_tiempo_folletos = rnd_f
                    self.eventos[f'Fin_Folletos_{v_id}_{siguiente.id}'] = self.reloj + t_folletos
                    self.metrica_total_folletos += 1
                else:
                    self.ventanillas[v_id]['libres'] += 1

            # --- SALIDA DE PINTURA ---
            elif evento_actual.startswith('Fin_Pintura_'):
                id_vis = int(evento_actual.split('_')[-1])
                visitante = self.visitantes_activos[id_vis]
                visitante.fin_pintura = self.reloj
                self.personas_en_pintura -= 1

                rnd_foto = random.random()
                visitante.rnd_decision_fotografia = rnd_foto

                if rnd_foto <= self.prob_fotografia:
                    visitante.fue_a_fotografia = True
                    self.metrica_total_fotografia += 1
                    self.personas_en_fotografia += 1

                    rnd_cerveza = random.random()
                    visitante.rnd_decision_cerveza = rnd_cerveza

                    if rnd_cerveza <= self.prob_cerveza:
                        visitante.tomo_cerveza = True
                        if self.servidores_cerveza > 0:
                            self.servidores_cerveza -= 1
                            min_c, max_c = self.parametros['cerveza']
                            t_servicio, rnd_s = self.generar_uniforme(min_c, max_c)
                            visitante.rnd_tiempo_cerveza = rnd_s
                            visitante.estado = "Siendo atendido (cerveza)"
                            visitante.sala_actual = "Stand Cerveza"
                            visitante.inicio_cerveza = self.reloj
                            self.eventos[f'Fin_Servicio_Cerveza_{visitante.id}'] = self.reloj + t_servicio
                        else:
                            visitante.inicio_cola_cerveza = self.reloj
                            visitante.estado = "En cola de cerveza"
                            visitante.sala_actual = "Cola Cerveza"
                            self.cola_cerveza.append(visitante)
                            self.max_cola_cerveza = max(self.max_cola_cerveza, len(self.cola_cerveza))
                         
                    else:
                        visitante.tomo_cerveza = False
                        visitante.estado = "En Fotografia"
                        visitante.sala_actual = "Fotografia"
                        visitante.inicio_fotografia = self.reloj
                        t_foto, rnd_foto1, rnd_foto2 = self.determinar_tiempo_sala("Fotografia")
                        visitante.rnd_tiempo_fotografia = (rnd_foto1, rnd_foto2)
                        self.eventos[f'Fin_Fotografia_{visitante.id}'] = self.reloj + t_foto
                else:
                    # Se va del sistema directamente tras pintura
                    visitante.fue_a_fotografia = False
                    visitante.estado = "Salio"
                    visitante.sala_actual = "Fuera"
                    visitante.reloj_salida = self.reloj
                    self.metrica_abandonos_post_pintura += 1

                    tiempo_permanencia = self.reloj - visitante.reloj_llegada
                    self.acumulador_tiempo_permanencia += tiempo_permanencia
                    self.visitantes_finalizados += 1

                    del self.visitantes_activos[visitante.id]

            # --- LE ENTREGAN LA CERVEZA (empieza la degustación) ---
            elif evento_actual.startswith('Fin_Servicio_Cerveza_'):
                id_vis = int(evento_actual.split('_')[-1])
                visitante = self.visitantes_activos[id_vis]
                visitante.fin_cerveza = self.reloj
                self.metrica_total_cervezas += 1
                self.metrica_suma_edades_cerveza += visitante.edad

                if len(self.cola_cerveza) > 0:
                    siguiente = self.cola_cerveza.pop(0)
                    min_c, max_c = self.parametros['cerveza']
                    t_servicio, rnd_s = self.generar_uniforme(min_c, max_c)
                    siguiente.rnd_tiempo_cerveza = rnd_s
                    siguiente.estado = "Siendo atendido (cerveza)"
                    siguiente.sala_actual = "Stand Cerveza"
                    siguiente.inicio_cerveza = self.reloj
                    self.eventos[f'Fin_Servicio_Cerveza_{siguiente.id}'] = self.reloj + t_servicio
                else:
                    self.servidores_cerveza += 1

                tiempo_degustacion, tabla_rk = calcular_tiempo_degustacion(visitante.edad, self.paso_h)
                self.tablas_rk_generadas[
                    f"Visitante {visitante.id} (Edad: {visitante.edad}, Dia {self.dia_actual})"
                ] = tabla_rk

                visitante.estado = "Degustando cerveza"
                visitante.sala_actual = "Stand Cerveza"
                visitante.inicio_degustacion = self.reloj
                self.eventos[f'Fin_Degustacion_{visitante.id}'] = self.reloj + tiempo_degustacion

            # --- TERMINA DE BEBER ---
            elif evento_actual.startswith('Fin_Degustacion_'):
                id_vis = int(evento_actual.split('_')[-1])
                visitante = self.visitantes_activos[id_vis]
                visitante.fin_degustacion = self.reloj

                visitante.estado = "En Fotografia"
                visitante.sala_actual = "Fotografia"
                visitante.inicio_fotografia = self.reloj
                t_foto, rnd_foto1, rnd_foto2 = self.determinar_tiempo_sala("Fotografia")
                visitante.rnd_tiempo_fotografia = (rnd_foto1, rnd_foto2)
                self.eventos[f'Fin_Fotografia_{visitante.id}'] = self.reloj + t_foto

            # --- FIN DE RECORRIDO (sale de fotografía) ---
            elif evento_actual.startswith('Fin_Fotografia_'):
                id_vis = int(evento_actual.split('_')[-1])
                visitante = self.visitantes_activos[id_vis]
                visitante.fin_fotografia = self.reloj
                visitante.estado = "Salio"
                visitante.sala_actual = "Fuera"
                visitante.reloj_salida = self.reloj
                self.personas_en_fotografia -= 1

                tiempo_permanencia = self.reloj - visitante.reloj_llegada
                self.acumulador_tiempo_permanencia += tiempo_permanencia
                self.visitantes_finalizados += 1

                del self.visitantes_activos[visitante.id]

            # --- CONTROL CADA 15 MINUTOS ---
            elif evento_actual == 'Control_15min':
                self.eventos['Control_15min'] = self.reloj + (15 * 60)
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
            fila = self._snapshot_sistema(evento_actual)
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
