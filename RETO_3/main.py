import sys

def procesar_linea(linea):

    partes = linea.split(",")

    if len(partes) != 4:
        return None

    producto = partes[1].strip()

    try:
        cantidad = int(partes[2].strip())
        precio = float(partes[3].strip())
    except ValueError:
        return None

    return (producto, cantidad, precio)


def agrupar_transacciones(lineas):

    productos = {}  

    for linea in lineas:
        linea = linea.strip()

        if not linea:
            continue

        resultado = procesar_linea(linea)
        if resultado is None:
            continue  

        producto, cantidad, precio = resultado

        if producto not in productos:
            productos[producto] = {
                "unidades": 0,
                "ingreso": 0.0
            }

        productos[producto]["unidades"] += cantidad
        productos[producto]["ingreso"] += cantidad * precio

    return productos


def calcular_promedios(productos):

    for producto in productos:
        unidades = productos[producto]["unidades"]
        ingreso = productos[producto]["ingreso"]

        productos[producto]["promedio"] = ingreso / unidades if unidades > 0 else 0.0

    return productos


def ordenar_por_ingreso(productos):

    return sorted(
        productos.items(),
        key=lambda x: x[1]["ingreso"],
        reverse=True
    )


def imprimir_csv(productos_ordenados):

    print("producto,unidades_vendidas,ingreso_total,precio_promedio")

    for nombre, datos in productos_ordenados:
        print(f"{nombre},{datos['unidades']},{datos['ingreso']:.2f},{datos['promedio']:.2f}")


def main():

    todas_las_lineas = sys.stdin.readlines()

    if len(todas_las_lineas) < 2:
        print("producto,unidades_vendidas,ingreso_total,precio_promedio")
        return

    lineas_de_datos = todas_las_lineas[1:]

    productos = agrupar_transacciones(lineas_de_datos)

    if not productos:
        print("producto,unidades_vendidas,ingreso_total,precio_promedio")
        return

    productos = calcular_promedios(productos)

    productos_ordenados = ordenar_por_ingreso(productos)

    imprimir_csv(productos_ordenados)

if __name__ == "__main__":
    main()