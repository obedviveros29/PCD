import numpy as np

np.random.seed(2024)
np.set_printoptions(precision=2, suppress=True)

categorias = ['Supermercados', 'Restaurantes', 'Gasolineras', 'Tiendas_Online', 'Entretenimiento']
numCategorias = len(categorias)

parametrosCategorias = {
    'Supermercados': (800, 400),
    'Restaurantes': (350, 150),
    'Gasolineras': (700, 250),
    'Tiendas_Online': (1200, 800),
    'Entretenimiento': (200, 100)
}

transaccionesPorCategoria = 500

transacciones = {}
idsTransaccion = {}

for indice, categoria in enumerate(categorias):
    media, desviacion = parametrosCategorias[categoria]
    montos = np.random.normal(media, desviacion, transaccionesPorCategoria)
    montos = np.maximum(montos, 10)
    anomaliasAltas = np.random.randint(8, 15)
    anomaliasBajas = np.random.randint(5, 10)
    indicesAltas = np.random.choice(transaccionesPorCategoria, anomaliasAltas, replace=False)
    montos[indicesAltas] = media + np.random.uniform(4, 8, anomaliasAltas) * desviacion
    indicesBajas = np.random.choice(
        [k for k in range(transaccionesPorCategoria) if k not in indicesAltas],
        anomaliasBajas, replace=False
    )
    montos[indicesBajas] = np.random.uniform(1, 15, anomaliasBajas)
    transacciones[categoria] = montos
    idsTransaccion[categoria] = np.arange(indice * 1000 + 1, indice * 1000 + transaccionesPorCategoria + 1)

montosMatriz = np.array([transacciones[categoria] for categoria in categorias])
todosMontos = np.concatenate([transacciones[categoria] for categoria in categorias])
todasCategorias = np.concatenate([[categoria] * transaccionesPorCategoria for categoria in categorias])
todosIds = np.concatenate([idsTransaccion[categoria] for categoria in categorias])

print("Datos generados")
print("montosMatriz shape:", montosMatriz.shape)
print("Total transacciones:", len(todosMontos))


print()
print("Estadisticas descriptivas por categoria")

medias = np.zeros(numCategorias)
medianas = np.zeros(numCategorias)
desviaciones = np.zeros(numCategorias)
minimos = np.zeros(numCategorias)
maximos = np.zeros(numCategorias)

for indice, categoria in enumerate(categorias):
    datos = montosMatriz[indice]
    medias[indice] = np.mean(datos)
    medianas[indice] = np.median(datos)
    desviaciones[indice] = np.std(datos)
    minimos[indice] = np.min(datos)
    maximos[indice] = np.max(datos)

print(f"{'Categoria':<20} {'Media':>12} {'Mediana':>12} {'Std':>12} {'Min':>10} {'Max':>10}")
for indice, categoria in enumerate(categorias):
    print(f"{categoria:<20} {medias[indice]:>11,.2f} {medianas[indice]:>11,.2f} {desviaciones[indice]:>11,.2f} {minimos[indice]:>9,.2f} {maximos[indice]:>9,.2f}")


print()
print("Cuartiles e IQR por categoria")

q1 = np.zeros(numCategorias)
q2 = np.zeros(numCategorias)
q3 = np.zeros(numCategorias)
iqr = np.zeros(numCategorias)

for indice, categoria in enumerate(categorias):
    datos = montosMatriz[indice]
    q1[indice] = np.percentile(datos, 25)
    q2[indice] = np.percentile(datos, 50)
    q3[indice] = np.percentile(datos, 75)
    iqr[indice] = q3[indice] - q1[indice]

print(f"{'Categoria':<20} {'Q1':>12} {'Q2':>12} {'Q3':>12} {'IQR':>12}")
for indice, categoria in enumerate(categorias):
    print(f"{categoria:<20} {q1[indice]:>11,.2f} {q2[indice]:>11,.2f} {q3[indice]:>11,.2f} {iqr[indice]:>11,.2f}")


print()
print("Limites para deteccion de outliers (IQR)")

factorIqr = 1.5
limitesInferiores = np.zeros(numCategorias)
limitesSuperiores = np.zeros(numCategorias)

for indice, categoria in enumerate(categorias):
    limitesInferiores[indice] = q1[indice] - factorIqr * iqr[indice]
    limitesSuperiores[indice] = q3[indice] + factorIqr * iqr[indice]

print(f"{'Categoria':<20} {'Limite Inf':>15} {'Limite Sup':>15}")
for indice, categoria in enumerate(categorias):
    print(f"{categoria:<20} {limitesInferiores[indice]:>14,.2f} {limitesSuperiores[indice]:>14,.2f}")


print()
print("Deteccion de outliers con IQR")

outliersIqr = {}
conteoOutliersIqr = np.zeros(numCategorias, dtype=int)

for indice, categoria in enumerate(categorias):
    datos = montosMatriz[indice]
    ids = idsTransaccion[categoria]
    mascaraOutliers = (datos < limitesInferiores[indice]) | (datos > limitesSuperiores[indice])
    mascaraInferiores = datos < limitesInferiores[indice]
    mascaraSuperiores = datos > limitesSuperiores[indice]
    outliersIqr[categoria] = {
        'ids': ids[mascaraOutliers],
        'montos': datos[mascaraOutliers],
        'total': int(np.sum(mascaraOutliers)),
        'inferiores': int(np.sum(mascaraInferiores)),
        'superiores': int(np.sum(mascaraSuperiores))
    }
    conteoOutliersIqr[indice] = int(np.sum(mascaraOutliers))

print(f"{'Categoria':<20} {'Total':>10} {'Outliers':>10} {'Porcentaje':>12} {'Inf':>8} {'Sup':>8}")
for indice, categoria in enumerate(categorias):
    porcentaje = (conteoOutliersIqr[indice] / transaccionesPorCategoria) * 100
    informacion = outliersIqr[categoria]
    print(f"{categoria:<20} {transaccionesPorCategoria:>10,} {informacion['total']:>10} {porcentaje:>11.1f}% {informacion['inferiores']:>8} {informacion['superiores']:>8}")

print("Total de outliers detectados:", int(np.sum(conteoOutliersIqr)))


print()
print("Analisis detallado de outliers (IQR)")

for categoria in categorias:
    informacion = outliersIqr[categoria]
    if informacion['total'] > 0:
        montosOutlier = informacion['montos']
        montoMinimoOutlier = np.min(montosOutlier)
        montoMaximoOutlier = np.max(montosOutlier)
        montoPromedioOutlier = np.mean(montosOutlier)
        print()
        print(categoria)
        print("   Outliers detectados:", informacion['total'])
        print(f"   Monto minimo outlier: {montoMinimoOutlier:,.2f}")
        print(f"   Monto maximo outlier: {montoMaximoOutlier:,.2f}")
        print(f"   Monto promedio outlier: {montoPromedioOutlier:,.2f}")
        if informacion['superiores'] > 0:
            indicesOrdenados = np.argsort(montosOutlier)[::-1]
            print("   Top 3 montos mas altos:")
            for j in range(min(3, len(indicesOrdenados))):
                idx = indicesOrdenados[j]
                print(f"      ID {informacion['ids'][idx]}: {montosOutlier[idx]:,.2f}")


print()
print("Calculo de z-scores por categoria")

umbralZscore = 3
zscoresMatriz = np.zeros_like(montosMatriz)

for indice, categoria in enumerate(categorias):
    datos = montosMatriz[indice]
    mediaCategoria = np.mean(datos)
    desviacionCategoria = np.std(datos)
    zscoresMatriz[indice] = (datos - mediaCategoria) / desviacionCategoria

print(f"{'Categoria':<20} {'Media Z':>10} {'Std Z':>10} {'Min Z':>10} {'Max Z':>10}")
for indice, categoria in enumerate(categorias):
    zs = zscoresMatriz[indice]
    print(f"{categoria:<20} {np.mean(zs):>10.4f} {np.std(zs):>10.4f} {np.min(zs):>10.2f} {np.max(zs):>10.2f}")


print()
print("Deteccion de outliers con z-score, umbral", umbralZscore)

outliersZscore = {}
conteoOutliersZscore = np.zeros(numCategorias, dtype=int)

for indice, categoria in enumerate(categorias):
    datos = montosMatriz[indice]
    zscores = zscoresMatriz[indice]
    ids = idsTransaccion[categoria]
    mascaraOutliersZ = np.abs(zscores) > umbralZscore
    mascaraZNegativos = zscores < -umbralZscore
    mascaraZPositivos = zscores > umbralZscore
    outliersZscore[categoria] = {
        'ids': ids[mascaraOutliersZ],
        'montos': datos[mascaraOutliersZ],
        'zscores': zscores[mascaraOutliersZ],
        'total': int(np.sum(mascaraOutliersZ)),
        'bajos': int(np.sum(mascaraZNegativos)),
        'altos': int(np.sum(mascaraZPositivos))
    }
    conteoOutliersZscore[indice] = int(np.sum(mascaraOutliersZ))

print(f"{'Categoria':<20} {'Total':>10} {'Outliers':>10} {'Porcentaje':>12} {'Z<-3':>8} {'Z>3':>8}")
for indice, categoria in enumerate(categorias):
    porcentaje = (conteoOutliersZscore[indice] / transaccionesPorCategoria) * 100
    informacion = outliersZscore[categoria]
    print(f"{categoria:<20} {transaccionesPorCategoria:>10,} {informacion['total']:>10} {porcentaje:>11.1f}% {informacion['bajos']:>8} {informacion['altos']:>8}")

print("Total de outliers detectados (z-score):", int(np.sum(conteoOutliersZscore)))


print()
print("Comparacion de metodos de deteccion")

totalIqr = int(np.sum(conteoOutliersIqr))
totalZscore = int(np.sum(conteoOutliersZscore))

print("   Metodo IQR:", totalIqr, "outliers detectados")
print("   Metodo Z-Score:", totalZscore, "outliers detectados")

print(f"{'Categoria':<20} {'IQR':>10} {'Z-Score':>10} {'Diferencia':>12} {'Coincidencia':>15}")
for indice, categoria in enumerate(categorias):
    nIqr = conteoOutliersIqr[indice]
    nZscore = conteoOutliersZscore[indice]
    diferencia = nIqr - nZscore
    idsIqr = set(outliersIqr[categoria]['ids'])
    idsZscore = set(outliersZscore[categoria]['ids'])
    coincidentes = len(idsIqr & idsZscore)
    print(f"{categoria:<20} {nIqr:>10} {nZscore:>10} {diferencia:>+12} {coincidentes:>15}")


print()
print("Reporte de transacciones sospechosas")
print("Alta prioridad, detectadas por ambos metodos")

totalAltaPrioridad = 0

for categoria in categorias:
    idsIqr = set(outliersIqr[categoria]['ids'])
    idsZscore = set(outliersZscore[categoria]['ids'])
    idsAmbos = idsIqr & idsZscore
    if len(idsAmbos) > 0:
        totalAltaPrioridad += len(idsAmbos)
        for transaccionId in list(idsAmbos)[:3]:
            idx = np.where(idsTransaccion[categoria] == transaccionId)[0][0]
            monto = montosMatriz[categorias.index(categoria), idx]
            zscore = zscoresMatriz[categorias.index(categoria), idx]
            print(f"   ID {transaccionId}: {categoria:15s} {monto:>10,.2f} (Z={zscore:+.2f})")

totalTransacciones = numCategorias * transaccionesPorCategoria
totalOutliersUnicos = sum(len(set(outliersIqr[c]['ids']) | set(outliersZscore[c]['ids'])) for c in categorias)
porcentajeAnomalias = (totalOutliersUnicos / totalTransacciones) * 100

print()
print("Resumen ejecutivo")
print("   Total transacciones analizadas:", totalTransacciones)
print(f"   Transacciones sospechosas: {totalOutliersUnicos} ({porcentajeAnomalias:.1f}%)")
print("   Alta prioridad (ambos metodos):", totalAltaPrioridad)


print()
print("Analisis de correlacion entre categorias")

matrizCorrelacion = np.corrcoef(montosMatriz)

print(f"{'':>18}", end='')
for categoria in categorias:
    print(f"{categoria[:8]:>10}", end='')
print()
for indice, categoria in enumerate(categorias):
    print(f"{categoria:<18}", end='')
    for j in range(numCategorias):
        print(f"{matrizCorrelacion[indice, j]:>10.3f}", end='')
    print()

correlacionMaxima = 0
parMaximo = ('', '')
for indice in range(numCategorias):
    for j in range(indice + 1, numCategorias):
        if abs(matrizCorrelacion[indice, j]) > abs(correlacionMaxima):
            correlacionMaxima = matrizCorrelacion[indice, j]
            parMaximo = (categorias[indice], categorias[j])

print()
print("Correlaciones mas fuertes")
print(f"   Mayor correlacion: {parMaximo[0]} - {parMaximo[1]}")
print(f"   Valor: {correlacionMaxima:.4f}")