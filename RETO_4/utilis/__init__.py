utils_init = '''
"""Utilidades del sistema de inventario."""
from .validators import validar_sku, validar_precio, validar_stock
from .io import leer_inventario, escribir_reporte
'''

print("=== models/__init__.py ===")
print(models_init)
print("\n=== utils/__init__.py ===")
print(utils_init)