#!/usr/bin/env python3

"""
Sistema de Inventario Modular
Genera reporte de productos que necesitan reorden.
"""

from models.producto import Producto
from utils.validators import validar_producto
from utils.io import leer_inventario, escribir_reporte

# Configuracion
ARCHIVO_INVENTARIO = "data/inventario.csv"
ARCHIVO_REPORTE = "outputs/reporte_inventario.csv"


def crear_productos(datos_raw):
    """
    Convierte lista de diccionarios en objetos Producto.
    Ignora registros invalidos.
    """
    productos = []
    
    for datos in datos_raw:
        # Validar
        es_valido, error = validar_producto(
            datos.get('sku'),
            datos.get('nombre'),
            datos.get('categoria'),
            datos.get('precio'),
            datos.get('stock'),
            datos.get('stock_minimo')
        )
        
        if not es_valido:
            print(f"Advertencia: Ignorando registro invalido - {error}")
            continue
        
        # Crear objeto Producto
        producto = Producto(
            sku=datos['sku'],
            nombre=datos['nombre'],
            categoria=datos['categoria'],
            precio=float(datos['precio']),
            stock=int(datos['stock']),
            stock_minimo=int(datos['stock_minimo'])
        )
        productos.append(producto)
    
    return productos


def filtrar_necesitan_reorden(productos):
    """Filtra productos que necesitan reorden."""
    return [p for p in productos if p.necesita_reorden()]


def ordenar_por_faltantes(productos):
    """Ordena por unidades faltantes (descendente)."""
    return sorted(productos, key=lambda p: p.unidades_faltantes(), reverse=True)


def main():
    print("=" * 50)
    print("SISTEMA DE INVENTARIO - Reporte de Reorden")
    print("=" * 50)
    
    # 1. Leer datos
    print(f"\nLeyendo inventario de: {ARCHIVO_INVENTARIO}")
    datos_raw = leer_inventario(ARCHIVO_INVENTARIO)
    print(f"Registros leidos: {len(datos_raw)}")
    
    # 2. Crear objetos Producto
    productos = crear_productos(datos_raw)
    print(f"Productos validos: {len(productos)}")
    
    # 3. Filtrar los que necesitan reorden
    necesitan_reorden = filtrar_necesitan_reorden(productos)
    print(f"Productos que necesitan reorden: {len(necesitan_reorden)}")
    
    # 4. Ordenar por unidades faltantes
    necesitan_reorden = ordenar_por_faltantes(necesitan_reorden)
    
    # 5. Mostrar resumen
    print("\n" + "-" * 50)
    print("PRODUCTOS QUE NECESITAN REORDEN:")
    print("-" * 50)
    for p in necesitan_reorden:
        print(p)
    
    # 6. Escribir reporte
    escribir_reporte(necesitan_reorden, ARCHIVO_REPORTE)
    print(f"\nReporte guardado en: {ARCHIVO_REPORTE}")
    
    print("\n" + "=" * 50)
    print("Proceso completado exitosamente")
    print("=" * 50)


if __name__ == "__main__":
    main()
