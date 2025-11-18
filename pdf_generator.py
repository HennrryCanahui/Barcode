import os
import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from barcode_tools import generar_code128_png, generar_qr_png
from utils import obtener_ruta_escritorio_real


def generar_codigos_barras_pdf(lista_productos_con_cantidades, nombre_archivo_salida=None, formato='barcode', area_cm2=1.8):
    """Genera un PDF con códigos (barcode o qr).

    - `lista_productos_con_cantidades`: lista de tuplas (codigo, cantidad, precio)
    - `formato`: 'barcode' o 'qr'
    - `area_cm2`: área del cuadrado (cm^2). Se interpreta como área = 1.8 -> lado = sqrt(1.8) cm
    """
    if nombre_archivo_salida is None:
        ruta_escritorio = obtener_ruta_escritorio_real()
        directorio_salida = os.path.join(ruta_escritorio, "codigos")
        os.makedirs(directorio_salida, exist_ok=True)
        nombre_archivo_salida = os.path.join(directorio_salida, "codigos_barras.pdf")
    else:
        directorio_salida = os.path.dirname(nombre_archivo_salida)
        if directorio_salida:
            os.makedirs(directorio_salida, exist_ok=True)

    if not lista_productos_con_cantidades:
        print("No hay productos para generar códigos de barras")
        return

    # Calcular lado del cuadrado en cm y en unidades reportlab
    lado_cm = math.sqrt(area_cm2)
    lado_rl = lado_cm * cm

    diccionario_imagenes = {}
    for codigo_producto, _, precio_producto in lista_productos_con_cantidades:
        if codigo_producto not in diccionario_imagenes:
            try:
                if formato == 'qr':
                    ruta_img = generar_qr_png(codigo_producto, tamaño_lado_cm=lado_cm)
                else:
                    ruta_img = generar_code128_png(codigo_producto)

                diccionario_imagenes[codigo_producto] = (ruta_img, precio_producto)
            except Exception as e:
                print(f"Error generando imagen para {codigo_producto}: {e}")
                continue

    if not diccionario_imagenes:
        print("No se pudieron generar imágenes")
        return

    lienzo_pdf = canvas.Canvas(nombre_archivo_salida, pagesize=letter)
    ancho_hoja, alto_hoja = letter

    # Márgenes mínimos
    MARGEN_SUPERIOR = 0.7 * cm
    MARGEN_INFERIOR = 0.5 * cm
    MARGEN_IZQUIERDO = 0.2 * cm
    MARGEN_DERECHO = 0.2 * cm

    area_util_ancho = ancho_hoja - MARGEN_IZQUIERDO - MARGEN_DERECHO
    area_util_alto = alto_hoja - MARGEN_SUPERIOR - MARGEN_INFERIOR

    # Queremos forzar 6 por fila como en la versión original
    CODIGOS_POR_FILA = 6
    ESPACIO_HORIZONTAL = 0.15 * cm
    ESPACIO_VERTICAL = 0.15 * cm
    ESPACIO_PRECIO = 0.25 * cm

    # Ajustar ancho para que cada elemento sea cuadrado del lado especificado
    ANCHO_CODIGO = lado_rl
    ALTO_CODIGO = lado_rl

    espacio_total_fila = (CODIGOS_POR_FILA * ANCHO_CODIGO) + ((CODIGOS_POR_FILA - 1) * ESPACIO_HORIZONTAL)
    if espacio_total_fila > area_util_ancho:
        # Recalcular ancho para caber 6 elementos
        espacio_disponible_codigos = area_util_ancho - ((CODIGOS_POR_FILA - 1) * ESPACIO_HORIZONTAL)
        ANCHO_CODIGO = espacio_disponible_codigos / CODIGOS_POR_FILA
        ALTO_CODIGO = ANCHO_CODIGO
        print(f"Ancho de código ajustado a: {ANCHO_CODIGO/cm:.2f} cm para garantizar 6 códigos por fila")

    offset_horizontal = max(0, (area_util_ancho - espacio_total_fila) / 2)

    x_inicial = MARGEN_IZQUIERDO + offset_horizontal
    y_inicial = alto_hoja - MARGEN_SUPERIOR

    x_actual = x_inicial
    y_actual = y_inicial
    codigo_en_fila = 0

    altura_elemento = 0.5 * cm + ESPACIO_PRECIO + ALTO_CODIGO

    for codigo_producto, cantidad_copias, _ in lista_productos_con_cantidades:
        if codigo_producto not in diccionario_imagenes:
            continue

        archivo_img, precio_producto = diccionario_imagenes[codigo_producto]
        for copia in range(cantidad_copias):
            if y_actual - altura_elemento < MARGEN_INFERIOR:
                lienzo_pdf.showPage()
                x_actual = x_inicial
                y_actual = y_inicial
                codigo_en_fila = 0

            if os.path.exists(archivo_img):
                texto_precio = f"2 x Q{precio_producto}"
                lienzo_pdf.setFont("Helvetica-Bold", 8)
                ancho_texto = lienzo_pdf.stringWidth(texto_precio, "Helvetica-Bold", 8)

                x_precio = x_actual + (ANCHO_CODIGO - ancho_texto) / 2
                y_precio = y_actual - 0.3 * cm
                lienzo_pdf.drawString(x_precio, y_precio, texto_precio)

                y_codigo = y_actual - 0.3 * cm - ESPACIO_PRECIO - ALTO_CODIGO

                lienzo_pdf.drawImage(
                    archivo_img,
                    x_actual,
                    y_codigo,
                    width=ANCHO_CODIGO,
                    height=ALTO_CODIGO,
                    preserveAspectRatio=True,
                    mask='auto'
                )

                codigo_en_fila += 1
                if codigo_en_fila < CODIGOS_POR_FILA:
                    x_actual += ANCHO_CODIGO + ESPACIO_HORIZONTAL
                else:
                    x_actual = x_inicial
                    y_actual -= altura_elemento + ESPACIO_VERTICAL
                    codigo_en_fila = 0
            else:
                print(f"Archivo de imagen no encontrado: {archivo_img}")

    lienzo_pdf.save()
    print(f"PDF generado exitosamente: {nombre_archivo_salida}")

    # Limpiar temporales generados por qr (y por barcode si fueron temporales)
    archivos_eliminados = 0
    for _, (ruta_img, _) in diccionario_imagenes.items():
        try:
            # No eliminar si el archivo está en el directorio de salida y es el resultado esperado
            if os.path.exists(ruta_img) and os.path.basename(ruta_img).startswith(('qr_', 'code128_', 'codigo_barra_')):
                os.remove(ruta_img)
                archivos_eliminados += 1
        except Exception as e:
            print(f"Error eliminando archivo temporal {ruta_img}: {e}")

    print(f"Archivos temporales eliminados: {archivos_eliminados}")
