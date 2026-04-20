# Calculadora de Sumas

Programa de línea de comandos que lee datos numéricos desde la entrada estándar, procesa cada línea calculando la suma de sus valores y muestra el resultado. Maneja datos "sucios": decimales, caracteres basura, espacios extra y líneas vacías.

---

## Instrucciones de uso

### Requisitos
- Python 3.x

### Ejecución

Puedes usar el programa de tres formas:

**1. Con un archivo de texto:**
```bash
python main.py < entrada.txt
```

**2. Escribiendo manualmente (terminar con Ctrl+D en Linux/Mac o Ctrl+Z en Windows):**
```bash
python main.py
```

**3. Guardando la salida en un archivo:**
```bash
python main.py < entrada.txt > salida.txt
```

---

## Ejemplo de entrada y salida

**Archivo `entrada.txt`:**
```
1,2,3
10

1.9,2.1,3.7
1a2,3b,4
-5,10,3
  5 , 10 , 15  
0,0,0
-1,-2,-3
abc,def
3.99
-0.5,0.5
,1,2,
100
```

**Salida esperada:**
```
6
10
0
6
19
8
30
0
-6
0
3
0
3
100
```

### Reglas de procesamiento

- **Línea vacía** → imprime `0`
- **Decimales** → se truncan antes de sumar (`3.9` → `3`, no `4`)
- **Caracteres basura** → se filtran (`1a2` → `12`)
- **Espacios extra** → se ignoran

---

## Autor

**Viveros Guzmán Obed**  
Licenciatura en Ciencia de Datos — IPN ESCOM  
Semestre Febrero-Julio 2026