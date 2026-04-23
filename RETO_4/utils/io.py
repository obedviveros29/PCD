
def leer_inventario(ruta_archivo):
    """
    Lee el archivo de inventario y retorna una lista de diccionarios.
    
    Args:
        ruta_archivo: Ruta al archivo CSV
        
    Returns:
        list: Lista de diccionarios con los datos de cada producto
        
    Raises:
        FileNotFoundError: Si el archivo no existe
    """
    productos_raw = []
    
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        lineas = archivo.readlines()
        
        # Primera linea son los encabezados
        if not lineas:
            return productos_raw
        
        encabezados = lineas[0].strip().split(',')
        
        # Procesar cada linea de datos
        for linea in lineas[1:]:
            linea = linea.strip()
            if not linea:
                continue
            
            valores = linea.split(',')
            if len(valores) == len(encabezados):
                producto_dict = dict(zip(encabezados, valores))
                productos_raw.append(producto_dict)
    
    return productos_raw


def escribir_reporte(productos, ruta_archivo):
    """
    Escribe el reporte de productos que necesitan reorden.
    
    Args:
        productos: Lista de objetos Producto
        ruta_archivo: Ruta donde guardar el CSV
    """
    encabezados = [
        "sku", "nombre", "categoria", "stock_actual", 
        "stock_minimo", "unidades_faltantes", "valor_inventario"
    ]
    
    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        # Escribir encabezados
        archivo.write(','.join(encabezados) + '\n')
        
        # Escribir datos
        for p in productos:
            linea = f"{p.sku},{p.nombre},{p.categoria},{p.stock},"
            linea += f"{p.stock_minimo},{p.unidades_faltantes()},{p.valor_inventario():.2f}"
            archivo.write(linea + '\n')

