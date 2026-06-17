class Producto:
    """
    Representa un producto en el inventario.
    
    Attributes:
        sku (str): Identificador unico
        nombre (str): Nombre del producto
        categoria (str): Categoria del producto
        precio (float): Precio unitario
        stock (int): Cantidad actual
        stock_minimo (int): Nivel minimo de stock
    """
    
    def __init__(self, sku, nombre, categoria, precio, stock, stock_minimo):
        """
        Inicializa un nuevo producto.
        
        Args:
            sku: Identificador unico del producto
            nombre: Nombre del producto
            categoria: Categoria del producto
            precio: Precio unitario (debe ser >= 0)
            stock: Cantidad actual (debe ser >= 0)
            stock_minimo: Nivel minimo de stock (debe ser >= 0)
        """
        self.sku = sku
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.stock_minimo = stock_minimo
    
    def necesita_reorden(self):
        """
        Determina si el producto necesita ser reordenado.
        
        Returns:
            bool: True si stock < stock_minimo, False en caso contrario
        """
        return self.stock < self.stock_minimo
    
    def unidades_faltantes(self):
        """
        Calcula cuantas unidades faltan para alcanzar el stock minimo.
        
        Returns:
            int: Unidades faltantes (0 si no necesita reorden)
        """
        if self.necesita_reorden():
            return self.stock_minimo - self.stock
        return 0
    
    def valor_inventario(self):
        """
        Calcula el valor monetario del inventario actual.
        
        Returns:
            float: precio * stock
        """
        return self.precio * self.stock
    
    def __str__(self):
        """Representacion legible para usuarios."""
        estado = "[REORDEN]" if self.necesita_reorden() else "[OK]"
        return f"{estado} {self.sku}: {self.nombre} - Stock: {self.stock}/{self.stock_minimo}"
    
    def __repr__(self):
        """Representacion tecnica para desarrolladores."""
        return (f"Producto('{self.sku}', '{self.nombre}', '{self.categoria}', "
                f"{self.precio}, {self.stock}, {self.stock_minimo})")