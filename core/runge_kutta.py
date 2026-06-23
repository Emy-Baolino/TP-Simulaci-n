import pandas as pd

def calcular_tiempo_degustacion(edad, h):
    """
    Integra numéricamente la ecuación diferencial:
        dC/dt = (t^2 - C) * h^2
    partiendo de C(0) = edad del visitante, usando el método de
    Runge-Kutta de 4to orden, hasta que dC/dt sea positiva.
    """
    t = 0.0
    C = float(edad)  # condición inicial C(0) = edad
    tabla_rk = []

    while True:
        dC_dt = ((t ** 2) - C) * (h ** 2)

        # 4 pendientes de Runge-Kutta de orden 4
        k1 = dC_dt
        k2 = (((t + h / 2) ** 2) - (C + (h / 2) * k1)) * (h ** 2)
        k3 = (((t + h / 2) ** 2) - (C + (h / 2) * k2)) * (h ** 2)
        k4 = (((t + h) ** 2) - (C + h * k3)) * (h ** 2)

        tabla_rk.append({
            "t": round(t, 4),
            "C(t)": round(C, 6),
            "dC/dt": round(dC_dt, 6),
            "k1": round(k1, 6),
            "k2": round(k2, 6),
            "k3": round(k3, 6),
            "k4": round(k4, 6)
        })

        # Cortamos cuando la velocidad de C se vuelve positiva
        if dC_dt > 0:
            break

        C_siguiente = C + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

        t += h
        C = C_siguiente

        if t > 50:
            break

    # Conversión a tiempo real: t = 1 equivale a 20 segundos
    tiempo_real_segundos = t * 20

    return tiempo_real_segundos, pd.DataFrame(tabla_rk)