import os
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from barcode import get_barcode_class
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import json
import qrcode
from PIL import Image

def cargar_ajustes(ruta="ajustes.json"):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

lista_productos_con_cantidades = []

def generar_codigo_qr(datos, nombre_archivo):
    """
    Genera un código QR optimizado para PDF (alta calidad, compatible con ReportLab)
    """
    # Asegurar extensión PNG
    if not nombre_archivo.lower().endswith(".png"):
        nombre_archivo += ".png"

    qr = qrcode.QRCode(
        version=None,  # Automático según contenido
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Mejor tolerancia
        box_size=12,   # Buena resolución para impresión
        border=2,
    )

    qr.add_data(datos)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGB")  # 🔑 CLAVE para ReportLab

    img.save(nombre_archivo, format="PNG")
    return nombre_archivo


def validar_ean13(codigo):
    """Valida y corrige código EAN-13"""
    codigo_str = str(codigo).strip()
    
    # Si tiene 12 dígitos, calcular dígito de control
    if len(codigo_str) == 12 and codigo_str.isdigit():
        suma_impares = sum(int(codigo_str[i]) for i in range(0, 12, 2))
        suma_pares = sum(int(codigo_str[i]) for i in range(1, 12, 2))
        total = suma_impares + (suma_pares * 3)
        digito_control = (10 - (total % 10)) % 10
        return codigo_str + str(digito_control)
    
    # Si tiene 13 dígitos, validar
    elif len(codigo_str) == 13 and codigo_str.isdigit():
        return codigo_str
    
    # Si no cumple, retornar None para que se maneje como error
    return None

def generar_codigos_barras_pdf(lista_productos_con_cantidades, nombre_archivo_salida=None):
    ajustes = cargar_ajustes()

    # ===============================
    # CONFIGURACIÓN DESDE JSON
    # ===============================
    MARGEN_SUPERIOR = ajustes["pdf"]["margenes"]["superior_cm"] * cm
    MARGEN_INFERIOR = ajustes["pdf"]["margenes"]["inferior_cm"] * cm
    MARGEN_IZQUIERDO = ajustes["pdf"]["margenes"]["izquierdo_cm"] * cm
    MARGEN_DERECHO = ajustes["pdf"]["margenes"]["derecho_cm"] * cm

    ANCHO_CODIGO = ajustes["codigo_barras"]["ancho_cm"] * cm
    ALTO_CODIGO = ajustes["codigo_barras"]["alto_cm"] * cm

    CODIGOS_POR_FILA = ajustes["grilla"]["codigos_por_fila"]
    ESPACIO_HORIZONTAL = ajustes["grilla"]["espacio_horizontal_cm"] * cm
    ESPACIO_VERTICAL = ajustes["grilla"]["espacio_vertical_cm"] * cm
    ESPACIO_PRECIO = ajustes["grilla"]["espacio_precio_cm"] * cm

    FUENTE_PRECIO = ajustes["precio"]["fuente"]
    TAMANO_PRECIO = ajustes["precio"]["tamano"]
    PREFIJO_PRECIO = ajustes["precio"]["prefijo"]
    OFFSET_PRECIO_Y = ajustes["precio"]["offset_y_cm"] * cm

    MOSTRAR_TEXTO_CODIGO = ajustes["codigo_barras"]["mostrar_texto"]
    TIPO_CODIGO = ajustes["codigo_barras"]["tipo"].lower()

    # ===============================
    # RUTA DE SALIDA
    # ===============================
    if nombre_archivo_salida is None:
        ruta_escritorio = obtener_ruta_escritorio_real()
        carpeta = ajustes["salida"]["carpeta"]
        nombre_pdf = ajustes["salida"]["nombre_pdf"]
        directorio_salida = os.path.join(ruta_escritorio, carpeta)
        os.makedirs(directorio_salida, exist_ok=True)
        nombre_archivo_salida = os.path.join(directorio_salida, nombre_pdf)

    # ===============================
    # GENERAR CÓDIGOS
    # ===============================
    diccionario_codigos_barras = {}
    errores = []
    
    for codigo_producto, _, precio_producto in lista_productos_con_cantidades:
        if codigo_producto not in diccionario_codigos_barras:
            try:
                nombre_archivo = f"codigo_{TIPO_CODIGO}_{codigo_producto}.png"
                
                if TIPO_CODIGO == "qr":
                    # Generar QR
                    ruta = generar_codigo_qr(str(codigo_producto), nombre_archivo)
                    diccionario_codigos_barras[codigo_producto] = (ruta, precio_producto)

                elif TIPO_CODIGO == "ean13":
                    # Validar y generar EAN-13
                    codigo_valido = validar_ean13(codigo_producto)
                    if codigo_valido:
                        generador = get_barcode_class('ean13')
                        imagen = generador(codigo_valido, writer=ImageWriter())
                        opciones = {"write_text": MOSTRAR_TEXTO_CODIGO}
                        ruta = imagen.save(f"codigo_barra_{codigo_producto}", opciones)
                        diccionario_codigos_barras[codigo_producto] = (ruta, precio_producto)
                    else:
                        errores.append(f"Código {codigo_producto} inválido para EAN-13 (debe ser 12 o 13 dígitos)")
                        continue
                        
                else:
                    # Code128 u otros códigos de barras
                    generador = get_barcode_class(TIPO_CODIGO)
                    imagen = generador(str(codigo_producto), writer=ImageWriter())
                    opciones = {"write_text": MOSTRAR_TEXTO_CODIGO}
                    ruta = imagen.save(f"codigo_barra_{codigo_producto}", opciones)
                    diccionario_codigos_barras[codigo_producto] = (ruta, precio_producto)
                    
            except Exception as e:
                errores.append(f"Error generando código {codigo_producto}: {str(e)}")
                continue

    # Mostrar errores si los hay
    if errores:
        print("\n⚠️ ADVERTENCIAS:")
        for error in errores:
            print(f"  - {error}")
        print()

    # Si no se generó ningún código, salir
    if not diccionario_codigos_barras:
        print("❌ No se pudo generar ningún código. Verifique los datos.")
        return

    # ===============================
    # PDF
    # ===============================
    lienzo_pdf = canvas.Canvas(nombre_archivo_salida, pagesize=letter)
    ancho_hoja, alto_hoja = letter

    area_util_ancho = ancho_hoja - MARGEN_IZQUIERDO - MARGEN_DERECHO
    area_util_alto = alto_hoja - MARGEN_SUPERIOR - MARGEN_INFERIOR

    espacio_total_fila = (CODIGOS_POR_FILA * ANCHO_CODIGO) + ((CODIGOS_POR_FILA - 1) * ESPACIO_HORIZONTAL)

    if espacio_total_fila > area_util_ancho:
        ANCHO_CODIGO = (area_util_ancho - ((CODIGOS_POR_FILA - 1) * ESPACIO_HORIZONTAL)) / CODIGOS_POR_FILA

    x_inicial = MARGEN_IZQUIERDO
    y_inicial = alto_hoja - MARGEN_SUPERIOR

    x_actual = x_inicial
    y_actual = y_inicial
    codigo_en_fila = 0
    altura_elemento = OFFSET_PRECIO_Y + ESPACIO_PRECIO + ALTO_CODIGO

    for codigo_producto, cantidad, _ in lista_productos_con_cantidades:
        # Saltar códigos que no se pudieron generar
        if codigo_producto not in diccionario_codigos_barras:
            continue
            
        ruta_img, precio = diccionario_codigos_barras[codigo_producto]

        for _ in range(cantidad):
            if y_actual - altura_elemento < MARGEN_INFERIOR:
                lienzo_pdf.showPage()
                x_actual = x_inicial
                y_actual = y_inicial
                codigo_en_fila = 0

            texto_precio = f"{PREFIJO_PRECIO}{precio}"
            lienzo_pdf.setFont(FUENTE_PRECIO, TAMANO_PRECIO)
            ancho_texto = lienzo_pdf.stringWidth(texto_precio, FUENTE_PRECIO, TAMANO_PRECIO)

            lienzo_pdf.drawString(
                x_actual + (ANCHO_CODIGO - ancho_texto) / 2,
                y_actual - OFFSET_PRECIO_Y,
                texto_precio
            )

            # Para QR, mantener aspecto cuadrado
            if TIPO_CODIGO == "qr":
                # Usar el menor valor entre ancho y alto para mantener cuadrado
                tamano_qr = min(ANCHO_CODIGO, ALTO_CODIGO)
                lienzo_pdf.drawImage(
                    ruta_img,
                    x_actual + (ANCHO_CODIGO - tamano_qr) / 2,  # Centrar horizontalmente
                    y_actual - OFFSET_PRECIO_Y - ESPACIO_PRECIO - tamano_qr,
                    width=tamano_qr,
                    height=tamano_qr,
                    preserveAspectRatio=True
                )
            else:
                lienzo_pdf.drawImage(
                    ruta_img,
                    x_actual,
                    y_actual - OFFSET_PRECIO_Y - ESPACIO_PRECIO - ALTO_CODIGO,
                    width=ANCHO_CODIGO,
                    height=ALTO_CODIGO
                )

            codigo_en_fila += 1
            if codigo_en_fila < CODIGOS_POR_FILA:
                x_actual += ANCHO_CODIGO + ESPACIO_HORIZONTAL
            else:
                x_actual = x_inicial
                y_actual -= altura_elemento + ESPACIO_VERTICAL
                codigo_en_fila = 0

    lienzo_pdf.save()
    print(f"✅ PDF generado exitosamente: {nombre_archivo_salida}")

    # Limpiar archivos temporales
    archivos_eliminados = 0
    for codigo_producto, (ruta_archivo_temporal, _) in diccionario_codigos_barras.items():
        try:
            if os.path.exists(ruta_archivo_temporal):
                os.remove(ruta_archivo_temporal)
                archivos_eliminados += 1
        except Exception as e:
            print(f"⚠️ Error eliminando archivo temporal {ruta_archivo_temporal}: {e}")
    
    print(f"🗑️ Archivos temporales eliminados: {archivos_eliminados}")

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