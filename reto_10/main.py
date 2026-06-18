import pandas as pd
import numpy as np
from typing import Dict, List


def estadisticas_basicas(precios):
    return {
        "precio_actual": float(precios.iloc[-1]),
        "precio_minimo": float(precios.min()),
        "precio_maximo": float(precios.max()),
        "precio_promedio": float(precios.mean()),
        "precio_mediana": float(precios.median()),
        "desviacion_std": float(precios.std()),
        "rango": float(precios.max() - precios.min()),
        "dias_analizados": int(len(precios))
    }


def calcular_rendimientos(precios):
    return precios.pct_change() * 100


def analisis_rendimientos(rendimientos):
    rendimientosLimpios = rendimientos.dropna()
    if len(rendimientosLimpios) == 0:
        return {
            "rendimiento_total": 0.0,
            "rendimiento_promedio": 0.0,
            "mejor_dia": None,
            "peor_dia": None,
            "dias_positivos": 0,
            "dias_negativos": 0,
            "volatilidad": 0.0
        }
    fechaMejor = rendimientosLimpios.idxmax()
    fechaPeor = rendimientosLimpios.idxmin()
    return {
        "rendimiento_total": float(rendimientosLimpios.sum()),
        "rendimiento_promedio": float(rendimientosLimpios.mean()),
        "mejor_dia": (str(fechaMejor.date()) if hasattr(fechaMejor, "date") else str(fechaMejor), float(rendimientosLimpios.max())),
        "peor_dia": (str(fechaPeor.date()) if hasattr(fechaPeor, "date") else str(fechaPeor), float(rendimientosLimpios.min())),
        "dias_positivos": int((rendimientosLimpios > 0).sum()),
        "dias_negativos": int((rendimientosLimpios < 0).sum()),
        "volatilidad": float(rendimientosLimpios.std())
    }


def media_movil(precios, ventana):
    return precios.rolling(window=ventana).mean()


def bandas_bollinger(precios, ventana=20, num_std=2):
    bandaMedia = precios.rolling(window=ventana).mean()
    desviacion = precios.rolling(window=ventana).std()
    return {
        "banda_superior": bandaMedia + num_std * desviacion,
        "banda_media": bandaMedia,
        "banda_inferior": bandaMedia - num_std * desviacion
    }


def detectar_maximos_minimos(precios, ventana=5):
    maximoMovil = precios.rolling(window=ventana * 2 + 1, center=True).max()
    minimoMovil = precios.rolling(window=ventana * 2 + 1, center=True).min()
    esMaximo = precios == maximoMovil
    esMinimo = precios == minimoMovil
    return {
        "maximos": precios[esMaximo],
        "minimos": precios[esMinimo]
    }


def clasificar_tendencia(precios, ventana=10):
    if len(precios) < ventana + 1:
        return "LATERAL"
    ma = media_movil(precios, ventana)
    precioActual = precios.iloc[-1]
    maActual = ma.iloc[-1]
    maAnterior = ma.iloc[-2]
    if pd.isna(maActual) or pd.isna(maAnterior):
        return "LATERAL"
    if precioActual > maActual and maActual > maAnterior:
        return "ALCISTA"
    if precioActual < maActual and maActual < maAnterior:
        return "BAJISTA"
    return "LATERAL"


def generar_senales_trading(precios, ma_corta=5, ma_larga=20):
    maCorta = media_movil(precios, ma_corta)
    maLarga = media_movil(precios, ma_larga)
    senales = pd.Series("MANTENER", index=precios.index)
    diferencia = maCorta - maLarga
    diferenciaPrevia = diferencia.shift(1)
    compras = (diferenciaPrevia <= 0) & (diferencia > 0)
    ventas = (diferenciaPrevia >= 0) & (diferencia < 0)
    senales[compras] = "COMPRA"
    senales[ventas] = "VENTA"
    return senales


def alertas_precio(precios, umbral_cambio=5.0):
    rendimientos = calcular_rendimientos(precios).dropna()
    alertas = []
    significativos = rendimientos[rendimientos.abs() > umbral_cambio]
    for fecha, cambio in significativos.items():
        fechaTexto = str(fecha.date()) if hasattr(fecha, "date") else str(fecha)
        alertas.append({
            "fecha": fechaTexto,
            "tipo": "SUBIDA" if cambio > 0 else "CAIDA",
            "cambio": float(cambio)
        })
    return alertas


def clasificar_volatilidad(rendimientos):
    desviacion = rendimientos.dropna().std()
    if pd.isna(desviacion):
        return "BAJA"
    if desviacion < 1:
        return "BAJA"
    if desviacion < 3:
        return "MEDIA"
    if desviacion < 5:
        return "ALTA"
    return "MUY ALTA"


def generar_reporte_completo(precios, nombre_accion):
    rendimientos = calcular_rendimientos(precios)
    estadisticas = estadisticas_basicas(precios)
    analisis = analisis_rendimientos(rendimientos)
    senales = generar_senales_trading(precios)
    fechaInicio = precios.index[0]
    fechaFin = precios.index[-1]
    return {
        "nombre": nombre_accion,
        "periodo": {
            "inicio": str(fechaInicio.date()) if hasattr(fechaInicio, "date") else str(fechaInicio),
            "fin": str(fechaFin.date()) if hasattr(fechaFin, "date") else str(fechaFin),
            "dias": int(len(precios))
        },
        "estadisticas": estadisticas,
        "rendimientos": analisis,
        "tendencia": clasificar_tendencia(precios),
        "volatilidad": clasificar_volatilidad(rendimientos),
        "senal_actual": str(senales.iloc[-1]),
        "alertas_recientes": alertas_precio(precios)
    }


def calcular_rsi(precios, periodos=14):
    cambios = precios.diff()
    ganancias = cambios.clip(lower=0)
    perdidas = -cambios.clip(upper=0)
    promedioGanancias = ganancias.rolling(window=periodos).mean()
    promedioPerdidas = perdidas.rolling(window=periodos).mean()
    rs = promedioGanancias / promedioPerdidas
    return 100 - (100 / (1 + rs))


def backtest_estrategia(precios, senales, capital_inicial=10000):
    capital = capital_inicial
    acciones = 0
    enPosicion = False
    precioCompra = 0.0
    numOperaciones = 0
    operacionesGanadoras = 0
    for fecha in precios.index:
        senal = senales.loc[fecha]
        precio = precios.loc[fecha]
        if senal == "COMPRA" and not enPosicion:
            acciones = capital / precio
            capital = 0.0
            precioCompra = precio
            enPosicion = True
        elif senal == "VENTA" and enPosicion:
            capital = acciones * precio
            acciones = 0
            enPosicion = False
            numOperaciones += 1
            if precio > precioCompra:
                operacionesGanadoras += 1
    if enPosicion:
        capital = acciones * precios.iloc[-1]
    rendimientoTotal = (capital - capital_inicial) / capital_inicial * 100
    return {
        "capital_final": float(capital),
        "rendimiento_total": float(rendimientoTotal),
        "num_operaciones": int(numOperaciones),
        "operaciones_ganadoras": int(operacionesGanadoras)
    }


def mostrar_reporte(reporte):
    print("=" * 70)
    print(f"           REPORTE DE ANALISIS: {reporte['nombre']}")
    print("=" * 70)
    periodo = reporte.get("periodo", {})
    print("\nPERIODO DE ANALISIS")
    print("-" * 40)
    print(f"Inicio: {periodo.get('inicio', 'N/A')}")
    print(f"Fin: {periodo.get('fin', 'N/A')}")
    print(f"Dias analizados: {periodo.get('dias', 'N/A')}")
    estadisticas = reporte.get("estadisticas", {})
    print("\nESTADISTICAS DE PRECIO")
    print("-" * 40)
    print(f"Precio actual:  ${estadisticas.get('precio_actual', 0):,.2f}")
    print(f"Precio minimo:  ${estadisticas.get('precio_minimo', 0):,.2f}")
    print(f"Precio maximo:  ${estadisticas.get('precio_maximo', 0):,.2f}")
    print(f"Precio promedio: ${estadisticas.get('precio_promedio', 0):,.2f}")
    rendimiento = reporte.get("rendimientos", {})
    print("\nRENDIMIENTO")
    print("-" * 40)
    print(f"Rendimiento total: {rendimiento.get('rendimiento_total', 0):+.2f}%")
    print(f"Rendimiento promedio diario: {rendimiento.get('rendimiento_promedio', 0):+.3f}%")
    if rendimiento.get("mejor_dia"):
        print(f"Mejor dia: {rendimiento['mejor_dia'][0]} ({rendimiento['mejor_dia'][1]:+.2f}%)")
    if rendimiento.get("peor_dia"):
        print(f"Peor dia: {rendimiento['peor_dia'][0]} ({rendimiento['peor_dia'][1]:+.2f}%)")
    print(f"Dias positivos: {rendimiento.get('dias_positivos', 0)}")
    print(f"Dias negativos: {rendimiento.get('dias_negativos', 0)}")
    print("\nINDICADORES")
    print("-" * 40)
    print(f"Tendencia: {reporte.get('tendencia', 'N/A')}")
    print(f"Volatilidad: {reporte.get('volatilidad', 'N/A')}")
    print(f"Senal actual: {reporte.get('senal_actual', 'N/A')}")
    alertas = reporte.get("alertas_recientes", [])
    if alertas:
        print("\nALERTAS RECIENTES")
        print("-" * 40)
        for alerta in alertas[-5:]:
            marca = "SUBIDA" if alerta["tipo"] == "SUBIDA" else "CAIDA"
            print(f"{alerta['fecha']}: {marca} de {alerta['cambio']:+.2f}%")
    print("\n" + "=" * 70)


def visualizar_precios_texto(precios, ancho=50):
    minimoPrecio = precios.min()
    maximoPrecio = precios.max()
    rango = maximoPrecio - minimoPrecio
    print(f"\nGrafico de precios: {precios.name}")
    print(f"Max: ${maximoPrecio:.2f}")
    print("-" * (ancho + 10))
    for fecha, precio in precios.iloc[::3].items():
        posicion = int((precio - minimoPrecio) / rango * ancho) if rango > 0 else ancho // 2
        barra = " " * posicion + "*"
        fechaTexto = fecha.strftime("%m/%d") if hasattr(fecha, "strftime") else str(fecha)[:5]
        print(f"{fechaTexto} |{barra}")
    print("-" * (ancho + 10))
    print(f"Min: ${minimoPrecio:.2f}")


np.random.seed(42)
fechas = pd.date_range(start="2024-01-01", periods=60, freq="B")
precioInicial = 100
rendimientosSimulados = np.random.normal(0.002, 0.02, 60)
preciosSimulados = precioInicial * np.cumprod(1 + rendimientosSimulados)
PRECIOS_ACCION = pd.Series(preciosSimulados.round(2), index=fechas, name="ACME Corp")

np.random.seed(123)
rendVolatil = np.random.normal(0, 0.05, 60)
preciosVolatil = 50 * np.cumprod(1 + rendVolatil)
ACCION_VOLATIL = pd.Series(preciosVolatil.round(2), index=fechas, name="VolatilTech")

rendBajista = np.random.normal(-0.005, 0.015, 60)
preciosBajista = 200 * np.cumprod(1 + rendBajista)
ACCION_BAJISTA = pd.Series(preciosBajista.round(2), index=fechas, name="DeclineCorp")


def main():
    print("Acciones disponibles para analisis:")
    print(f"1. ACME Corp - Precio actual: ${PRECIOS_ACCION.iloc[-1]:.2f}")
    print(f"2. VolatilTech - Precio actual: ${ACCION_VOLATIL.iloc[-1]:.2f}")
    print(f"3. DeclineCorp - Precio actual: ${ACCION_BAJISTA.iloc[-1]:.2f}")

    print("\nPRUEBA DE FUNCIONES INDIVIDUALES")
    print("=" * 50)

    print("\n-- Estadisticas Basicas --")
    print(estadisticas_basicas(PRECIOS_ACCION))

    print("\n-- Rendimientos (primeros 5) --")
    rendimientos = calcular_rendimientos(PRECIOS_ACCION)
    print(rendimientos.head())

    print("\n-- Analisis de Rendimientos --")
    print(analisis_rendimientos(rendimientos))

    print("\n-- Media Movil (5 dias) --")
    print(media_movil(PRECIOS_ACCION, 5).tail())

    print("\n-- Bandas de Bollinger --")
    bandas = bandas_bollinger(PRECIOS_ACCION, 20, 2)
    for nombre, serie in bandas.items():
        if serie is not None:
            print(f"{nombre}: {serie.iloc[-1]:.2f}")

    print("\n-- Tendencia --")
    print(f"Tendencia actual: {clasificar_tendencia(PRECIOS_ACCION)}")

    print("\nGENERANDO REPORTE COMPLETO\n")
    reporte = generar_reporte_completo(PRECIOS_ACCION, "ACME Corp")
    mostrar_reporte(reporte)

    print("\n" + "=" * 70)
    print("         COMPARACION DE ACCIONES")
    print("=" * 70)
    acciones = [
        (PRECIOS_ACCION, "ACME Corp"),
        (ACCION_VOLATIL, "VolatilTech"),
        (ACCION_BAJISTA, "DeclineCorp")
    ]
    for precios, nombre in acciones:
        rendimientos = calcular_rendimientos(precios)
        if rendimientos is not None:
            rendimientoTotal = rendimientos.sum() if not rendimientos.isna().all() else 0
            volatilidad = clasificar_volatilidad(rendimientos)
            tendencia = clasificar_tendencia(precios)
            print(f"\n{nombre}:")
            print(f"  Rendimiento: {rendimientoTotal:+.2f}%")
            print(f"  Volatilidad: {volatilidad}")
            print(f"  Tendencia: {tendencia}")

    print("\n-- RSI (ultimos 5) --")
    print(calcular_rsi(PRECIOS_ACCION).tail())

    print("\n-- Backtest estrategia ACME Corp --")
    senales = generar_senales_trading(PRECIOS_ACCION)
    print(backtest_estrategia(PRECIOS_ACCION, senales))


if __name__ == "__main__":
    main()