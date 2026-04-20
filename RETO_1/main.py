import sys

def limpiar(texto):
    caracteres_validos = '0123456789,-'
    resultado = ''
    for char in texto:
        if char in caracteres_validos:
            resultado += char
    return resultado

def convertir_entero(texto):
    texto = limpiar(texto.strip())
    if not texto: 
        return 0
    try: 
        return int(float(texto))
    except ValueError:
        return 0
    
def procesar_linea(linea):
    if not linea.strip():
        return 0
    
    valores = linea.split(',')
    total = sum(convertir_entero(v) for v in valores)
    return total

def main():
    for linea in sys.stdin:
        linea = linea.rstrip('\n')
        print(procesar_linea(linea))

if __name__  == '__main__':
    main()
    