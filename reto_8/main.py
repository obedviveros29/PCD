import numpy as np

np.random.seed(42)

estaciones = ['Coyoacan', 'Azcapotzalco', 'Xochimilco', 'Tlalpan', 'Miguel Hidalgo']
n_estaciones = len(estaciones)
n_dias = 7
n_horas = 24

temp_base = np.array([22, 24, 20, 19, 23])
hora_del_dia = np.arange(24)
variacion_diaria = 5 * np.sin((hora_del_dia - 6) * np.pi / 12)

temperatura = np.zeros((n_estaciones, n_dias, n_horas))
for i in range(n_estaciones):
    for d in range(n_dias):
        temperatura[i, d, :] = temp_base[i] + variacion_diaria + np.random.normal(0, 1.5, n_horas)

temperatura[1, 2, 10:14] = np.nan
temperatura[3, 5, 0:3] = np.nan

humedad_base = np.array([55, 45, 70, 65, 50])
variacion_humedad = -15 * np.sin((hora_del_dia - 6) * np.pi / 12)

humedad = np.zeros((n_estaciones, n_dias, n_horas))
for i in range(n_estaciones):
    for d in range(n_dias):
        humedad[i, d, :] = humedad_base[i] + variacion_humedad + np.random.normal(0, 5, n_horas)

humedad = np.clip(humedad, 20, 95)
humedad[0, 4, 15:18] = np.nan

co2_base = np.array([380, 420, 360, 350, 410])
patron_trafico = np.zeros(24)
patron_trafico[7:10] = 30
patron_trafico[17:20] = 40
patron_trafico[12:14] = 15

co2 = np.zeros((n_estaciones, n_dias, n_horas))
for i in range(n_estaciones):
    for d in range(n_dias):
        co2[i, d, :] = co2_base[i] + patron_trafico + np.random.normal(0, 10, n_horas)

co2[:, 3, :] *= 1.15
co2[2, 1, 5:8] = np.nan

temp_promedio_diario = np.nanmean(temperatura, axis=2)
humedad_promedio_diario = np.nanmean(humedad, axis=2)
co2_promedio_diario = np.nanmean(co2, axis=2)


print("PARTE 1: EXPLORACION DE ARRAYS")
print("-" * 40)

n_dimensiones = temperatura.ndim
forma = temperatura.shape
total_elementos = temperatura.size
tipo_datos = temperatura.dtype
memoria_bytes = temperatura.nbytes

print(f"Dimensiones: {n_dimensiones}D")
print(f"Forma: {forma}")
print(f"Total de mediciones: {total_elementos}")
print(f"Tipo de datos: {tipo_datos}")
print(f"Memoria: {memoria_bytes} bytes")

temp_coyoacan_d1_12h = temperatura[0, 0, 12]
temp_xochimilco_d3 = temperatura[2, 2, :]
temp_mh_7dias = temp_promedio_diario[4, :]
ultimo_co2 = co2[-1, -1, -1]

print(f"\nCoyoacan, Dia 1, 12:00h: {temp_coyoacan_d1_12h:.1f} C")
print(f"Xochimilco, Dia 3, primeras 6 horas: {temp_xochimilco_d3[:6].round(1)}")
print(f"Miguel Hidalgo, promedio por dia: {temp_mh_7dias.round(1)}")
print(f"Ultimo CO2 registrado: {ultimo_co2:.1f} ppm")

temp_tardes = temperatura[:, :, 12:18]
humedad_subset = humedad[:3, -3:, :]
co2_mananas_pares = co2[::2, :, 6:12]
temp_inverso = temperatura[:, ::-1, :]

print(f"\nTemperaturas tardes (12-17h) shape: {temp_tardes.shape}")
print(f"Subset humedad shape: {humedad_subset.shape}")
print(f"CO2 mananas estaciones pares shape: {co2_mananas_pares.shape}")
print(f"Temperatura dias invertidos shape: {temp_inverso.shape}")


print("\nPARTE 2: ESTADISTICAS BASICAS")
print("-" * 40)

temp_promedio = np.nanmean(temperatura)
temp_maxima = np.nanmax(temperatura)
temp_minima = np.nanmin(temperatura)
temp_std = np.nanstd(temperatura)
temp_rango = temp_maxima - temp_minima

print(f"Promedio: {temp_promedio:.2f} C")
print(f"Maxima: {temp_maxima:.2f} C")
print(f"Minima: {temp_minima:.2f} C")
print(f"Desv. Est.: {temp_std:.2f} C")
print(f"Rango: {temp_rango:.2f} C")

temp_por_estacion = np.nanmean(temperatura, axis=(1, 2))
humedad_por_hora = np.nanmean(humedad, axis=(0, 1))
co2_max_por_dia = np.nanmax(co2, axis=(0, 2))

print("\nTemperatura promedio por estacion:")
for i, est in enumerate(estaciones):
    print(f"  {est}: {temp_por_estacion[i]:.1f} C")

print("\nHumedad promedio por hora (00, 06, 12, 18):")
for h in [0, 6, 12, 18]:
    print(f"  {h:02d}:00 - {humedad_por_hora[h]:.1f}%")

print("\nCO2 maximo por dia:")
for d in range(n_dias):
    print(f"  Dia {d+1}: {co2_max_por_dia[d]:.1f} ppm")


print("\nPARTE 3: OPERACIONES VECTORIZADAS")
print("-" * 40)

temperatura_fahrenheit = temperatura * 9 / 5 + 32
temperatura_kelvin = temperatura + 273.15
humedad_min = np.nanmin(humedad)
humedad_max = np.nanmax(humedad)
humedad_normalizada = (humedad - humedad_min) / (humedad_max - humedad_min)

print(f"Temperatura promedio Fahrenheit: {np.nanmean(temperatura_fahrenheit):.1f} F")
print(f"Temperatura promedio Kelvin: {np.nanmean(temperatura_kelvin):.1f} K")
print(f"Humedad normalizada promedio: {np.nanmean(humedad_normalizada):.3f}")

ict = temperatura + 0.05 * humedad
n_frio = np.sum(ict < 20)
n_confortable = np.sum((ict >= 20) & (ict < 25))
n_calido = np.sum((ict >= 25) & (ict < 30))
n_muy_caluroso = np.sum(ict >= 30)
n_validas = np.sum(~np.isnan(ict))

print(f"\nIndice de Confort Termico promedio: {np.nanmean(ict):.2f}")
print("Distribucion de condiciones:")
print(f"  Frio (<20): {n_frio} ({100*n_frio/n_validas:.1f}%)")
print(f"  Confortable (20-25): {n_confortable} ({100*n_confortable/n_validas:.1f}%)")
print(f"  Calido (25-30): {n_calido} ({100*n_calido/n_validas:.1f}%)")
print(f"  Muy caluroso (>=30): {n_muy_caluroso} ({100*n_muy_caluroso/n_validas:.1f}%)")


print("\nPARTE 4: ANALISIS AVANZADO")
print("-" * 40)

co2_media = np.nanmean(co2)
co2_std = np.nanstd(co2)
limite_inferior = co2_media - 2 * co2_std
limite_superior = co2_media + 2 * co2_std

mascara_anomalias = (~np.isnan(co2)) & ((co2 < limite_inferior) | (co2 > limite_superior))
n_anomalias = np.sum(mascara_anomalias)

print(f"Media CO2: {co2_media:.1f} ppm")
print(f"Desv. Est.: {co2_std:.1f} ppm")
print(f"Limite inferior: {limite_inferior:.1f} ppm")
print(f"Limite superior: {limite_superior:.1f} ppm")
print(f"Anomalias detectadas: {n_anomalias}")

DIA_CONTINGENCIA = 3
co2_contingencia = co2[:, DIA_CONTINGENCIA, :]
dias_normales = [0, 1, 2, 4, 5, 6]
co2_dias_normales = co2[:, dias_normales, :]

promedio_contingencia = np.nanmean(co2_contingencia)
promedio_normal = np.nanmean(co2_dias_normales)
incremento_porcentual = ((promedio_contingencia - promedio_normal) / promedio_normal) * 100

co2_por_estacion_contingencia = np.nanmean(co2_contingencia, axis=1)
co2_por_estacion_normal = np.nanmean(co2_dias_normales, axis=(1, 2))
incremento_por_estacion = ((co2_por_estacion_contingencia - co2_por_estacion_normal) /
                           co2_por_estacion_normal) * 100
idx_mas_afectada = np.argmax(incremento_por_estacion)

print(f"\nAnalisis de contingencia (Dia 4):")
print(f"  CO2 promedio contingencia: {promedio_contingencia:.1f} ppm")
print(f"  CO2 promedio dias normales: {promedio_normal:.1f} ppm")
print(f"  Incremento: {incremento_porcentual:.1f}%")
print(f"  Estacion mas afectada: {estaciones[idx_mas_afectada]}")


print("\nREPORTE EJECUTIVO")
print("-" * 40)

idx_mas_calurosa = np.argmax(np.nanmean(temperatura, axis=(1, 2)))
idx_mas_humeda = np.argmax(np.nanmean(humedad, axis=(1, 2)))
idx_mejor_aire = np.argmin(np.nanmean(co2, axis=(1, 2)))

temp_por_hora = np.nanmean(temperatura, axis=(0, 1))
hora_mas_calurosa = np.argmax(temp_por_hora)
co2_por_hora = np.nanmean(co2, axis=(0, 1))
hora_peor_aire = np.argmax(co2_por_hora)

nan_temperatura = np.sum(np.isnan(temperatura))
nan_humedad = np.sum(np.isnan(humedad))
nan_co2 = np.sum(np.isnan(co2))
total_nan = nan_temperatura + nan_humedad + nan_co2

print(f"Temperatura promedio: {np.nanmean(temperatura):.1f} C")
print(f"Humedad promedio: {np.nanmean(humedad):.1f}%")
print(f"CO2 promedio: {np.nanmean(co2):.1f} ppm")
print(f"Estacion mas calurosa: {estaciones[idx_mas_calurosa]}")
print(f"Estacion mas humeda: {estaciones[idx_mas_humeda]}")
print(f"Mejor calidad de aire: {estaciones[idx_mejor_aire]}")
print(f"Hora mas calurosa: {hora_mas_calurosa:02d}:00 hrs")
print(f"Hora con mas CO2: {hora_peor_aire:02d}:00 hrs")
print(f"Valores faltantes totales: {total_nan}")
print(f"  Temperatura: {nan_temperatura}")
print(f"  Humedad: {nan_humedad}")
print(f"  CO2: {nan_co2}")