import sys

def farenheit_a_celsius(f):
    return (f - 32) * 5.0/9.0

def clasificar_temperatura(c):
    if c < 0:
        return "Congelante"
    elif 0 < c <= 15:
        return "Frío"
    elif 15 < c <= 25:
        return "Templado"
    elif 25 < c <= 35:
        return "Caliente"
    else:
        return "Extremo"    

def main():
    # Leer y descartar encabezado de entrada
    primera_linea = True
    
    # Imprimir encabezado de salida
    print("ciudad,temperatura_celsius,clasificacion")
    
    for linea in sys.stdin:
        linea = linea.strip()
        
        # Saltar encabezado
        if primera_linea:
            primera_linea = False
            continue
        
        # Saltar lineas vacias
        if not linea:
            continue
        
        # Separar campos
        partes = linea.split(',')
        if len(partes) != 3:
            continue  # Ignorar linea invalida
        
        ciudad = partes[0]
        temp_str = partes[1]
        unidad = partes[2].strip().upper()
        
        # Validar unidad
        if unidad not in ['C', 'F']:
            continue  # Ignorar
        
        # Convertir temperatura
        try:
            temp = float(temp_str)
        except ValueError:
            continue  # Ignorar si no es numero
        
        # Convertir a Celsius
        if unidad == 'F':
            celsius = farenheit_a_celsius(temp)
        else:
            celsius = temp
        
        # Clasificar y imprimir
        clasificacion = clasificar_temperatura(celsius)
        print(f"{ciudad},{celsius:.1f},{clasificacion}")

if __name__ == "__main__":
    main()