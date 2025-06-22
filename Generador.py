import os
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from barcode import get_barcode_class
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

#import time

# Detecta correctamente el escritorio visible (OneDrive o local)
lista_productos_con_cantidades = []

def generar_codigos_barras_pdf(lista_productos_con_cantidades, nombre_archivo_salida=None):
    """
    Genera un PDF con códigos de barras organizados en una grilla
    
    Args:
        lista_productos_con_cantidades: Lista de tuplas (codigo, cantidad, precio)
        nombre_archivo_salida: Ruta del archivo PDF de salida
    """
    # Ruta por defecto: carpeta "codigos" en el escritorio visible
    if nombre_archivo_salida is None:
        ruta_escritorio = obtener_ruta_escritorio_real()
        directorio_salida = os.path.join(ruta_escritorio, "codigos")
        os.makedirs(directorio_salida, exist_ok=True)
        nombre_archivo_salida = os.path.join(directorio_salida, "codigos_barras.pdf")
    else:
        directorio_salida = os.path.dirname(nombre_archivo_salida)
        if directorio_salida:  # Solo crear si hay un directorio especificado
            os.makedirs(directorio_salida, exist_ok=True)

    # Verificar que hay productos para procesar
    if not lista_productos_con_cantidades:
        print("No hay productos para generar códigos de barras")
        return

    # Generar códigos de barras únicos
    diccionario_codigos_barras = {}
    for codigo_producto, _, precio_producto in lista_productos_con_cantidades:
        if codigo_producto not in diccionario_codigos_barras:
            try:
                generador_code128 = get_barcode_class('code128')
                imagen_codigo_barra = generador_code128(
                    str(codigo_producto),
                    writer=ImageWriter()
                )
                nombre_archivo_temporal = f"codigo_barra_{codigo_producto}.png"
                opciones_imagen = {'write_text': False}  # Desactiva el número debajo del código de barras
                ruta_archivo_completa = imagen_codigo_barra.save(nombre_archivo_temporal, opciones_imagen)
                diccionario_codigos_barras[codigo_producto] = (ruta_archivo_completa, precio_producto)
            except Exception as e:
                print(f"Error generando código de barras para {codigo_producto}: {e}")
                continue

    if not diccionario_codigos_barras:
        print("No se pudieron generar códigos de barras")
        return

    # Crear el PDF con los códigos de barras
    lienzo_pdf = canvas.Canvas(nombre_archivo_salida, pagesize=letter)
    ancho_hoja, alto_hoja = letter
    
    # Configuración de márgenes y dimensiones (mínimos para impresión)
    MARGEN_SUPERIOR = 0.7 * cm
    MARGEN_INFERIOR = 0.5 * cm
    MARGEN_IZQUIERDO = 0.2 * cm  # Mínimo para impresión
    MARGEN_DERECHO = 0.2 * cm    # Mínimo para impresión
    
    # Área útil de la hoja (respetando márgenes)
    area_util_ancho = ancho_hoja - MARGEN_IZQUIERDO - MARGEN_DERECHO
    area_util_alto = alto_hoja - MARGEN_SUPERIOR - MARGEN_INFERIOR
    
    # Dimensiones optimizadas para 6 códigos por fila
    ANCHO_CODIGO = 3.3 * cm  # Reducido ligeramente para garantizar espacio
    ALTO_CODIGO = 1 * cm
    
    # Espaciado mínimo entre elementos
    ESPACIO_HORIZONTAL = 0.15 * cm  # Reducido para maximizar espacio
    ESPACIO_VERTICAL = 0.15 * cm
    ESPACIO_PRECIO = 0.25 * cm
    
    # Configuración de la grilla - FORZAR 6 códigos por fila
    CODIGOS_POR_FILA = 6
    
    # Calcular el espacio total requerido por fila
    espacio_total_fila = (CODIGOS_POR_FILA * ANCHO_CODIGO) + ((CODIGOS_POR_FILA - 1) * ESPACIO_HORIZONTAL)
    
    # Verificar que caben 6 códigos, si no, ajustar el ancho del código
    if espacio_total_fila > area_util_ancho:
        # Recalcular ancho del código para que quepan exactamente 6
        espacio_disponible_codigos = area_util_ancho - ((CODIGOS_POR_FILA - 1) * ESPACIO_HORIZONTAL)
        ANCHO_CODIGO = espacio_disponible_codigos / CODIGOS_POR_FILA
        espacio_total_fila = area_util_ancho  # Usar todo el ancho disponible
        print(f"Ancho de código ajustado a: {ANCHO_CODIGO/cm:.2f} cm para garantizar 6 códigos por fila")
    
    # Calcular offset para centrar horizontalmente (mínimo centrado)
    offset_horizontal = max(0, (area_util_ancho - espacio_total_fila) / 2)
    
    # Posiciones iniciales (respetando márgenes)
    x_inicial = MARGEN_IZQUIERDO + offset_horizontal
    y_inicial = alto_hoja - MARGEN_SUPERIOR
    
    # Variables de control
    x_actual = x_inicial
    y_actual = y_inicial
    codigo_en_fila = 0
    
    # Altura total de cada elemento (precio + espacio + código de barras)
    altura_elemento = 0.5 * cm + ESPACIO_PRECIO + ALTO_CODIGO

    # Procesar cada producto
    for codigo_producto, cantidad_copias, _ in lista_productos_con_cantidades:
        if codigo_producto not in diccionario_codigos_barras:
            continue
            
        archivo_codigo_barra, precio_producto = diccionario_codigos_barras[codigo_producto]
        
        for copia in range(cantidad_copias):
            # Verificar si el código de barras cabe en la página actual
            if y_actual - altura_elemento < MARGEN_INFERIOR:
                # Nueva página
                lienzo_pdf.showPage()
                x_actual = x_inicial
                y_actual = y_inicial
                codigo_en_fila = 0

            if os.path.exists(archivo_codigo_barra):
                # Preparar texto del precio
                texto_precio = f"Q{precio_producto}"
                
                # Configurar fuente para el precio
                lienzo_pdf.setFont("Helvetica-Bold", 14)
                ancho_texto = lienzo_pdf.stringWidth(texto_precio, "Helvetica-Bold", 14)
                
                # Posición del precio (centrado sobre el código de barras)
                x_precio = x_actual + (ANCHO_CODIGO - ancho_texto) / 2
                y_precio = y_actual - 0.4 * cm
                
                # Dibujar el precio
                lienzo_pdf.drawString(x_precio, y_precio, texto_precio)
                
                # Posición del código de barras
                y_codigo = y_actual - 0.4 * cm - ESPACIO_PRECIO - ALTO_CODIGO
                
                # Dibujar el código de barras
                lienzo_pdf.drawImage(
                    archivo_codigo_barra,
                    x_actual,
                    y_codigo,
                    width=ANCHO_CODIGO,
                    height=ALTO_CODIGO
                )
                
                # Actualizar posición para el siguiente código
                codigo_en_fila += 1
                
                if codigo_en_fila < CODIGOS_POR_FILA:
                    # Mover a la siguiente posición horizontal
                    x_actual += ANCHO_CODIGO + ESPACIO_HORIZONTAL
                else:
                    # Saltar a la siguiente fila
                    x_actual = x_inicial
                    y_actual -= altura_elemento + ESPACIO_VERTICAL
                    codigo_en_fila = 0
                    
            else:
                print(f"Archivo de código de barras no encontrado: {archivo_codigo_barra}")

    # Guardar el PDF
    lienzo_pdf.save()
    print(f"PDF generado exitosamente: {nombre_archivo_salida}")

    # Limpiar archivos temporales
    archivos_eliminados = 0
    for codigo_producto, (ruta_archivo_temporal, _) in diccionario_codigos_barras.items():
        try:
            if os.path.exists(ruta_archivo_temporal):
                os.remove(ruta_archivo_temporal)
                archivos_eliminados += 1
        except Exception as e:
            print(f"Error eliminando archivo temporal {ruta_archivo_temporal}: {e}")
    
    print(f"Archivos temporales eliminados: {archivos_eliminados}")

def obtener_ruta_escritorio_real():
    """Función auxiliar para obtener la ruta del escritorio"""
    import os
    import ctypes
    from ctypes import wintypes
    CSIDL_DESKTOP = 0  # Escritorio
    SHGFP_TYPE_CURRENT = 0

    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf)

    return buf.value

# Llamar a la función con la lista correcta
#generar_codigos_barras_pdf(id_copias_list)




#end = time.time()
#print(f"Tiempo de ejecución: {end - start} segundos")


#
## nota: Cambiar el generador envez de generar n cantidad de veses el codigo MEJOR generar uno por codigo
##       y copiarlo y pegarlo n cantidad de veces. Hennrry 30/10/2024 |°_°|
#

## superar cant 384 en 13s

## Harreglado cant 384 en 0.1s