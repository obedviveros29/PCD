import pandas as pd
import numpy as np
import json
from datetime import datetime


def cargar_datos():
    estudiantes = pd.DataFrame({
        "boleta": ["2021630001", "2021630002", "2021630003", "2021630004", "2021630005",
                   "2022630001", "2022630002", "2022630003", "2022630004", "2022630005",
                   "2023630001", "2023630002", "2023630003", "2023630004", "2023630005"],
        "nombre": ["Juan Pérez García", "María López Ruiz", "Pedro Sánchez Torres",
                   "Ana Martínez Díaz", "Luis Rodríguez Vega", "Carmen Flores Luna",
                   "Roberto Díaz Mora", "Laura Torres Silva", "Diego Ramírez Cruz",
                   "Sofía Vargas Romo", "Carlos Mendoza Ríos", "Patricia Ortiz León",
                   "Miguel Ángel Castro", "Fernanda Reyes Paz", "Andrés Guzmán Villa"],
        "semestre": [4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2],
        "carrera": ["CD"] * 15,
        "email": ["juan.perez@ipn.mx", "maria.lopez@ipn.mx", "pedro.sanchez@ipn.mx",
                  "ana.martinez@ipn.mx", "luis.rodriguez@ipn.mx", "carmen.flores@ipn.mx",
                  "roberto.diaz@ipn.mx", "laura.torres@ipn.mx", "diego.ramirez@ipn.mx",
                  "sofia.vargas@ipn.mx", "carlos.mendoza@ipn.mx", "patricia.ortiz@ipn.mx",
                  "miguel.castro@ipn.mx", "fernanda.reyes@ipn.mx", "andres.guzman@ipn.mx"]
    })

    materias = pd.DataFrame({
        "materia_id": ["MAT101", "MAT102", "PROG101", "PROG102", "EST101", "EST102", "BD101"],
        "nombre": ["Cálculo Diferencial", "Cálculo Integral", "Programación I",
                   "Programación II", "Probabilidad", "Estadística Inferencial",
                   "Bases de Datos"],
        "creditos": [8, 8, 6, 6, 6, 6, 6],
        "semestre_materia": [1, 2, 1, 2, 2, 3, 3]
    })

    np.random.seed(42)
    calificaciones_data = []

    for boleta in estudiantes["boleta"]:
        semestre = estudiantes[estudiantes["boleta"] == boleta]["semestre"].values[0]
        materias_cursadas = materias[materias["semestre_materia"] <= semestre]["materia_id"].tolist()

        for materia in materias_cursadas:
            base = np.random.uniform(5, 10)
            parcial_uno = round(min(10, max(0, base + np.random.normal(0, 1))), 1)
            parcial_dos = round(min(10, max(0, base + np.random.normal(0, 1))), 1)
            final = round(min(10, max(0, base + np.random.normal(0, 0.5))), 1)

            if np.random.random() < 0.05:
                parcial_dos = np.nan

            calificaciones_data.append({
                "boleta": boleta,
                "materia_id": materia,
                "parcial_1": parcial_uno,
                "parcial_2": parcial_dos,
                "final": final
            })

    calificaciones = pd.DataFrame(calificaciones_data)

    return estudiantes, calificaciones, materias


def calcular_promedios_estudiantes(df_calificaciones):
    columnas_calificacion = ["parcial_1", "parcial_2", "final"]
    base = df_calificaciones.copy()
    base["promedio_materia"] = base[columnas_calificacion].mean(axis=1)
    promedios = base.groupby("boleta", as_index=False)["promedio_materia"].mean()
    promedios = promedios.rename(columns={"promedio_materia": "promedio"})
    promedios["promedio"] = promedios["promedio"].round(2)
    return promedios


def contar_reprobadas_estudiantes(df_calificaciones):
    columnas_calificacion = ["parcial_1", "parcial_2", "final"]
    base = df_calificaciones.copy()
    base["promedio_materia"] = base[columnas_calificacion].mean(axis=1)
    base["reprobada"] = base["promedio_materia"] < 6
    reprobadas = base.groupby("boleta", as_index=False)["reprobada"].sum()
    reprobadas = reprobadas.rename(columns={"reprobada": "reprobadas"})
    reprobadas["reprobadas"] = reprobadas["reprobadas"].astype(int)
    return reprobadas


def info_general(df_estudiantes, df_calificaciones):
    semestres = sorted(df_estudiantes["semestre"].unique().tolist())
    return {
        "total_estudiantes": len(df_estudiantes),
        "total_registros_calif": len(df_calificaciones),
        "semestres": semestres,
        "materias_con_registros": df_calificaciones["materia_id"].nunique()
    }


def validar_datos(df_calificaciones):
    columnas_calificacion = ["parcial_1", "parcial_2", "final"]
    registros_con_nulos = int(df_calificaciones[columnas_calificacion].isna().any(axis=1).sum())
    fuera_rango = (df_calificaciones[columnas_calificacion] < 0) | (df_calificaciones[columnas_calificacion] > 10)
    calificaciones_fuera_rango = int(fuera_rango.sum().sum())
    datos_validos = registros_con_nulos == 0 and calificaciones_fuera_rango == 0
    return {
        "registros_con_nulos": registros_con_nulos,
        "calificaciones_fuera_rango": calificaciones_fuera_rango,
        "datos_validos": datos_validos
    }


def buscar_estudiante(df_estudiantes, criterio, valor):
    if criterio == "boleta":
        return df_estudiantes[df_estudiantes["boleta"] == valor].reset_index(drop=True)
    if criterio == "nombre":
        coincidencias = df_estudiantes["nombre"].str.contains(valor, case=False, na=False)
        return df_estudiantes[coincidencias].reset_index(drop=True)
    if criterio == "semestre":
        return df_estudiantes[df_estudiantes["semestre"] == int(valor)].reset_index(drop=True)
    return df_estudiantes.iloc[0:0]


def obtener_kardex(boleta, df_estudiantes, df_calificaciones, df_materias):
    resultado = {
        "estudiante": None,
        "materias": None,
        "promedio_general": None,
        "creditos_cursados": None,
        "materias_aprobadas": None,
        "materias_reprobadas": None
    }
    registro_estudiante = df_estudiantes[df_estudiantes["boleta"] == boleta]
    if registro_estudiante.empty:
        return resultado
    resultado["estudiante"] = registro_estudiante.iloc[0].to_dict()
    calificaciones_estudiante = df_calificaciones[df_calificaciones["boleta"] == boleta].copy()
    if calificaciones_estudiante.empty:
        resultado["materias"] = calificaciones_estudiante
        resultado["promedio_general"] = 0.0
        resultado["creditos_cursados"] = 0
        resultado["materias_aprobadas"] = 0
        resultado["materias_reprobadas"] = 0
        return resultado
    columnas_calificacion = ["parcial_1", "parcial_2", "final"]
    calificaciones_estudiante["promedio"] = calificaciones_estudiante[columnas_calificacion].mean(axis=1).round(2)
    detalle = calificaciones_estudiante.merge(
        df_materias[["materia_id", "nombre", "creditos"]],
        on="materia_id", how="left"
    )
    detalle = detalle.rename(columns={"nombre": "materia"})
    detalle["estado"] = detalle["promedio"].apply(lambda promedio: "Aprobada" if promedio >= 6 else "Reprobada")
    columnas_kardex = ["materia_id", "materia", "creditos", "parcial_1", "parcial_2", "final", "promedio", "estado"]
    resultado["materias"] = detalle[columnas_kardex].reset_index(drop=True)
    resultado["promedio_general"] = round(detalle["promedio"].mean(), 2)
    resultado["creditos_cursados"] = int(detalle["creditos"].sum())
    resultado["materias_aprobadas"] = int((detalle["estado"] == "Aprobada").sum())
    resultado["materias_reprobadas"] = int((detalle["estado"] == "Reprobada").sum())
    return resultado


def filtrar_por_rendimiento(df_calificaciones, df_estudiantes, min_promedio=None, max_promedio=None):
    promedios = calcular_promedios_estudiantes(df_calificaciones)
    resultado = promedios.merge(df_estudiantes, on="boleta", how="left")
    if min_promedio is not None:
        resultado = resultado[resultado["promedio"] >= min_promedio]
    if max_promedio is not None:
        resultado = resultado[resultado["promedio"] <= max_promedio]
    columnas = ["boleta", "nombre", "semestre", "promedio"]
    return resultado[columnas].sort_values("promedio", ascending=False).reset_index(drop=True)


def calcular_promedio_materia(df_calificaciones, materia_id):
    resultado = {
        "materia": materia_id,
        "inscritos": None,
        "promedio_parcial1": None,
        "promedio_parcial2": None,
        "promedio_final": None,
        "promedio_general": None,
        "tasa_aprobacion": None,
        "calificacion_maxima": None,
        "calificacion_minima": None
    }
    registros = df_calificaciones[df_calificaciones["materia_id"] == materia_id].copy()
    if registros.empty:
        return resultado
    columnas_calificacion = ["parcial_1", "parcial_2", "final"]
    registros["promedio_materia"] = registros[columnas_calificacion].mean(axis=1)
    aprobados = (registros["promedio_materia"] >= 6).sum()
    resultado["inscritos"] = int(len(registros))
    resultado["promedio_parcial1"] = round(registros["parcial_1"].mean(), 2)
    resultado["promedio_parcial2"] = round(registros["parcial_2"].mean(), 2)
    resultado["promedio_final"] = round(registros["final"].mean(), 2)
    resultado["promedio_general"] = round(registros["promedio_materia"].mean(), 2)
    resultado["tasa_aprobacion"] = round(aprobados / len(registros) * 100, 1)
    resultado["calificacion_maxima"] = round(registros["promedio_materia"].max(), 2)
    resultado["calificacion_minima"] = round(registros["promedio_materia"].min(), 2)
    return resultado


def ranking_estudiantes(df_calificaciones, df_estudiantes, top_n=10):
    promedios = calcular_promedios_estudiantes(df_calificaciones)
    ranking = promedios.merge(df_estudiantes[["boleta", "nombre", "semestre"]], on="boleta", how="left")
    ranking = ranking.sort_values("promedio", ascending=False).head(top_n).reset_index(drop=True)
    ranking.insert(0, "posicion", range(1, len(ranking) + 1))
    columnas = ["posicion", "boleta", "nombre", "semestre", "promedio"]
    return ranking[columnas]


def estadisticas_por_semestre(df_estudiantes, df_calificaciones):
    promedios = calcular_promedios_estudiantes(df_calificaciones)
    promedios = promedios.merge(df_estudiantes[["boleta", "semestre"]], on="boleta", how="left")
    columnas_calificacion = ["parcial_1", "parcial_2", "final"]
    calificaciones = df_calificaciones.copy()
    calificaciones["promedio_materia"] = calificaciones[columnas_calificacion].mean(axis=1)
    calificaciones = calificaciones.merge(df_estudiantes[["boleta", "semestre"]], on="boleta", how="left")
    calificaciones["aprobada"] = calificaciones["promedio_materia"] >= 6
    resumen = promedios.groupby("semestre")["promedio"].agg(
        estudiantes="count", promedio="mean", mejor_promedio="max", peor_promedio="min"
    )
    tasa = calificaciones.groupby("semestre")["aprobada"].mean().mul(100).round(1)
    resumen["tasa_aprobacion"] = tasa
    resumen["promedio"] = resumen["promedio"].round(2)
    resumen["mejor_promedio"] = resumen["mejor_promedio"].round(2)
    resumen["peor_promedio"] = resumen["peor_promedio"].round(2)
    return resumen[["estudiantes", "promedio", "tasa_aprobacion", "mejor_promedio", "peor_promedio"]]


def identificar_estudiantes_riesgo(df_calificaciones, df_estudiantes, umbral_promedio=7.0, max_reprobadas=2):
    promedios = calcular_promedios_estudiantes(df_calificaciones)
    reprobadas = contar_reprobadas_estudiantes(df_calificaciones)
    base = promedios.merge(reprobadas, on="boleta", how="left")
    base = base.merge(df_estudiantes[["boleta", "nombre", "semestre"]], on="boleta", how="left")
    base["bajo_promedio"] = base["promedio"] < umbral_promedio
    base["exceso_reprobadas"] = base["reprobadas"] > max_reprobadas
    en_riesgo = base[base["bajo_promedio"] | base["exceso_reprobadas"]].copy()

    def asignar_motivo(fila):
        if fila["bajo_promedio"] and fila["exceso_reprobadas"]:
            return "Ambos"
        if fila["bajo_promedio"]:
            return "Bajo promedio"
        return "Materias reprobadas"

    en_riesgo["motivo"] = en_riesgo.apply(asignar_motivo, axis=1)
    columnas = ["boleta", "nombre", "semestre", "promedio", "reprobadas", "motivo"]
    return en_riesgo[columnas].sort_values("promedio").reset_index(drop=True)


def generar_reporte_academico(df_estudiantes, df_calificaciones, df_materias):
    promedios = calcular_promedios_estudiantes(df_calificaciones)
    columnas_calificacion = ["parcial_1", "parcial_2", "final"]
    calificaciones = df_calificaciones.copy()
    calificaciones["promedio_materia"] = calificaciones[columnas_calificacion].mean(axis=1)
    tasa_global = round((calificaciones["promedio_materia"] >= 6).mean() * 100, 1)
    resumen_general = {
        "total_estudiantes": len(df_estudiantes),
        "promedio_global": round(promedios["promedio"].mean(), 2),
        "tasa_aprobacion": tasa_global
    }
    por_materia = pd.DataFrame(
        [calcular_promedio_materia(df_calificaciones, materia) for materia in df_materias["materia_id"]]
    )
    return {
        "resumen_general": resumen_general,
        "por_semestre": estadisticas_por_semestre(df_estudiantes, df_calificaciones),
        "por_materia": por_materia,
        "mejores_estudiantes": ranking_estudiantes(df_calificaciones, df_estudiantes, top_n=5),
        "estudiantes_riesgo": identificar_estudiantes_riesgo(df_calificaciones, df_estudiantes),
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def exportar_kardex(boleta, kardex, formato="csv"):
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"kardex_{boleta}_{marca_tiempo}.{formato}"
    if formato == "csv":
        kardex["materias"].to_csv(nombre_archivo, index=False)
    elif formato == "json":
        materias = kardex["materias"].where(pd.notnull(kardex["materias"]), None).to_dict(orient="records")
        contenido = {
            "estudiante": kardex["estudiante"],
            "materias": materias,
            "promedio_general": kardex["promedio_general"],
            "creditos_cursados": kardex["creditos_cursados"],
            "materias_aprobadas": kardex["materias_aprobadas"],
            "materias_reprobadas": kardex["materias_reprobadas"]
        }
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(contenido, archivo, ensure_ascii=False, indent=2)
    return nombre_archivo


def predecir_riesgo_proximo_semestre(df_calificaciones, df_estudiantes):
    base = df_calificaciones.copy()
    base["tendencia_decreciente"] = (base["parcial_1"] > base["parcial_2"]) & (base["parcial_2"] > base["final"])
    base["final_menor_inicio"] = base["final"] < base["parcial_1"]
    base["senal_riesgo"] = base["tendencia_decreciente"] | base["final_menor_inicio"]
    senales = base.groupby("boleta", as_index=False)["senal_riesgo"].sum()
    senales = senales.rename(columns={"senal_riesgo": "materias_en_descenso"})
    totales = base.groupby("boleta", as_index=False)["materia_id"].count()
    totales = totales.rename(columns={"materia_id": "total_materias"})
    resultado = senales.merge(totales, on="boleta", how="left")
    resultado = resultado.merge(df_estudiantes[["boleta", "nombre", "semestre"]], on="boleta", how="left")
    resultado["materias_en_descenso"] = resultado["materias_en_descenso"].astype(int)
    resultado["proporcion_descenso"] = (resultado["materias_en_descenso"] / resultado["total_materias"]).round(2)
    resultado = resultado[resultado["materias_en_descenso"] > 0]
    columnas = ["boleta", "nombre", "semestre", "materias_en_descenso", "total_materias", "proporcion_descenso"]
    return resultado[columnas].sort_values("proporcion_descenso", ascending=False).reset_index(drop=True)


def comparar_estudiantes(boleta1, boleta2, df_calificaciones, df_estudiantes, df_materias):
    kardex_uno = obtener_kardex(boleta1, df_estudiantes, df_calificaciones, df_materias)
    kardex_dos = obtener_kardex(boleta2, df_estudiantes, df_calificaciones, df_materias)
    if kardex_uno["estudiante"] is None or kardex_dos["estudiante"] is None:
        return {"error": "Alguna de las boletas no existe"}
    resumen = pd.DataFrame([
        {
            "boleta": boleta1,
            "nombre": kardex_uno["estudiante"]["nombre"],
            "promedio_general": kardex_uno["promedio_general"],
            "materias_aprobadas": kardex_uno["materias_aprobadas"],
            "materias_reprobadas": kardex_uno["materias_reprobadas"],
            "creditos_cursados": kardex_uno["creditos_cursados"]
        },
        {
            "boleta": boleta2,
            "nombre": kardex_dos["estudiante"]["nombre"],
            "promedio_general": kardex_dos["promedio_general"],
            "materias_aprobadas": kardex_dos["materias_aprobadas"],
            "materias_reprobadas": kardex_dos["materias_reprobadas"],
            "creditos_cursados": kardex_dos["creditos_cursados"]
        }
    ])
    if kardex_uno["promedio_general"] > kardex_dos["promedio_general"]:
        mejor_promedio = kardex_uno["estudiante"]["nombre"]
    elif kardex_dos["promedio_general"] > kardex_uno["promedio_general"]:
        mejor_promedio = kardex_dos["estudiante"]["nombre"]
    else:
        mejor_promedio = "Empate"
    materias_comunes = set(kardex_uno["materias"]["materia_id"]) & set(kardex_dos["materias"]["materia_id"])
    return {
        "resumen": resumen,
        "mejor_promedio": mejor_promedio,
        "diferencia_promedio": round(abs(kardex_uno["promedio_general"] - kardex_dos["promedio_general"]), 2),
        "materias_comunes": sorted(materias_comunes)
    }


def mostrar_kardex(kardex):
    if kardex["estudiante"] is None:
        print("Estudiante no encontrado")
        return
    estudiante = kardex["estudiante"]
    print("KARDEX ACADEMICO")
    print(f"Boleta: {estudiante.get('boleta', 'N/A')}")
    print(f"Nombre: {estudiante.get('nombre', 'N/A')}")
    print(f"Semestre: {estudiante.get('semestre', 'N/A')}")
    print(f"Carrera: {estudiante.get('carrera', 'N/A')}")
    print(f"Email: {estudiante.get('email', 'N/A')}")
    print()
    print("Calificaciones")
    if kardex["materias"] is not None and len(kardex["materias"]) > 0:
        print(kardex["materias"].to_string(index=False))
    else:
        print("Sin calificaciones registradas")
    print()
    print("Resumen")
    print(f"Promedio general: {kardex.get('promedio_general', 0):.2f}")
    print(f"Creditos cursados: {kardex.get('creditos_cursados', 0)}")
    print(f"Materias aprobadas: {kardex.get('materias_aprobadas', 0)}")
    print(f"Materias reprobadas: {kardex.get('materias_reprobadas', 0)}")


def mostrar_reporte(reporte):
    print("REPORTE ACADEMICO - CIENCIA DE DATOS")
    print(f"Generado: {reporte['fecha_generacion']}")
    print()
    resumen = reporte.get("resumen_general", {})
    print("Resumen general")
    print(f"Total de estudiantes: {resumen.get('total_estudiantes', 'N/A')}")
    print(f"Promedio global: {resumen.get('promedio_global', 0):.2f}")
    print(f"Tasa de aprobacion: {resumen.get('tasa_aprobacion', 0):.1f}%")
    print()
    if reporte.get("por_semestre") is not None:
        print("Estadisticas por semestre")
        print(reporte["por_semestre"].to_string())
        print()
    if reporte.get("mejores_estudiantes") is not None:
        print("Top estudiantes")
        print(reporte["mejores_estudiantes"].to_string(index=False))
        print()
    if reporte.get("estudiantes_riesgo") is not None and len(reporte["estudiantes_riesgo"]) > 0:
        print(f"Estudiantes en riesgo ({len(reporte['estudiantes_riesgo'])})")
        print(reporte["estudiantes_riesgo"].to_string(index=False))
    else:
        print("No hay estudiantes en riesgo academico")


def main():
    df_estudiantes, df_calificaciones, df_materias = cargar_datos()

    print("Datos cargados")
    print(f"Estudiantes: {len(df_estudiantes)}")
    print(f"Calificaciones: {len(df_calificaciones)}")
    print(f"Materias: {len(df_materias)}")
    print()

    print("Informacion general")
    print(info_general(df_estudiantes, df_calificaciones))
    print()

    print("Validacion de datos")
    print(validar_datos(df_calificaciones))
    print()

    print("Busqueda por nombre 'María'")
    print(buscar_estudiante(df_estudiantes, "nombre", "María").to_string(index=False))
    print()

    kardex = obtener_kardex("2021630001", df_estudiantes, df_calificaciones, df_materias)
    mostrar_kardex(kardex)
    print()

    print("Filtrado por promedio entre 7.0 y 8.0")
    print(filtrar_por_rendimiento(df_calificaciones, df_estudiantes, 7.0, 8.0).to_string(index=False))
    print()

    print("Estadisticas de la materia PROG101")
    print(calcular_promedio_materia(df_calificaciones, "PROG101"))
    print()

    print("Ranking de estudiantes")
    print(ranking_estudiantes(df_calificaciones, df_estudiantes, top_n=5).to_string(index=False))
    print()

    reporte = generar_reporte_academico(df_estudiantes, df_calificaciones, df_materias)
    mostrar_reporte(reporte)
    print()

    archivo_csv = exportar_kardex("2021630001", kardex, "csv")
    archivo_json = exportar_kardex("2021630001", kardex, "json")
    print(f"Kardex exportado: {archivo_csv}")
    print(f"Kardex exportado: {archivo_json}")
    print()

    print("Prediccion de riesgo proximo semestre")
    print(predecir_riesgo_proximo_semestre(df_calificaciones, df_estudiantes).to_string(index=False))
    print()

    comparacion = comparar_estudiantes("2021630001", "2021630002", df_calificaciones, df_estudiantes, df_materias)
    print("Comparacion entre estudiantes")
    print(comparacion["resumen"].to_string(index=False))
    print(f"Mejor promedio: {comparacion['mejor_promedio']}")
    print(f"Diferencia de promedio: {comparacion['diferencia_promedio']}")
    print(f"Materias comunes: {comparacion['materias_comunes']}")


if __name__ == "__main__":
    main()