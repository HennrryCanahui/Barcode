
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter, A4, legal
from barcode import get_barcode_class
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os
import json
import qrcode
from PIL import Image
from Funciones import obtener_ruta_escritorio_real, cargar_ajustes


lista_productos_con_cantidades = []

def generar_codigo_qr(datos, nombre_archivo):
    """Genera un código QR optimizado para PDF (alta calidad)"""
    if not nombre_archivo.lower().endswith(".png"):
        nombre_archivo += ".png"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=2,
    )

    qr.add_data(datos)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGB")

    img.save(nombre_archivo, format="PNG")
    return nombre_archivo

def validar_codigo(codigo, tipo_codigo):
    """
    Valida códigos según su tipo y retorna el código válido o None
    """
    codigo_str = str(codigo).strip()
    
    if tipo_codigo == "ean13":
        # EAN-13: 12 o 13 dígitos
        if len(codigo_str) == 12 and codigo_str.isdigit():
            suma_impares = sum(int(codigo_str[i]) for i in range(0, 12, 2))
            suma_pares = sum(int(codigo_str[i]) for i in range(1, 12, 2))
            total = suma_impares + (suma_pares * 3)
            digito_control = (10 - (total % 10)) % 10
            return codigo_str + str(digito_control)
        elif len(codigo_str) == 13 and codigo_str.isdigit():
            return codigo_str
        return None
    
    elif tipo_codigo == "ean8":
        # EAN-8: 7 u 8 dígitos
        if len(codigo_str) == 7 and codigo_str.isdigit():
            suma_impares = sum(int(codigo_str[i]) for i in range(0, 7, 2))
            suma_pares = sum(int(codigo_str[i]) for i in range(1, 7, 2))
            total = (suma_impares * 3) + suma_pares
            digito_control = (10 - (total % 10)) % 10
            return codigo_str + str(digito_control)
        elif len(codigo_str) == 8 and codigo_str.isdigit():
            return codigo_str
        return None
    
    elif tipo_codigo == "upca":
        # UPC-A: 11 o 12 dígitos
        if len(codigo_str) == 11 and codigo_str.isdigit():
            suma_impares = sum(int(codigo_str[i]) for i in range(0, 11, 2))
            suma_pares = sum(int(codigo_str[i]) for i in range(1, 11, 2))
            total = (suma_impares * 3) + suma_pares
            digito_control = (10 - (total % 10)) % 10
            return codigo_str + str(digito_control)
        elif len(codigo_str) == 12 and codigo_str.isdigit():
            return codigo_str
        return None
    
    elif tipo_codigo in ["code39", "code93"]:
        # Code39/Code93: Solo mayúsculas, números y algunos símbolos
        codigo_upper = codigo_str.upper()
        caracteres_validos = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. $/+%"
        if all(c in caracteres_validos for c in codigo_upper):
            return codigo_upper
        return None
    
    elif tipo_codigo == "code128":
        # Code128: Acepta casi cualquier carácter ASCII
        return codigo_str
    
    elif tipo_codigo == "itf":
        # ITF (Interleaved 2 of 5): Solo números, longitud par
        if codigo_str.isdigit() and len(codigo_str) % 2 == 0:
            return codigo_str
        return None
    
    # Por defecto, aceptar el código tal cual
    return codigo_str

def generar_codigos_barras_pdf(lista_productos_con_cantidades, nombre_archivo_salida=None):
    ajustes = cargar_ajustes()

    # ===============================
    # CONFIGURACIÓN DESDE JSON
    # ===============================
    # Obtener tamaño de página
    pagesize_config = ajustes["pdf"]["pagesize"].upper()
    if pagesize_config == "A4":
        page_size = A4
    elif pagesize_config == "LEGAL":
        page_size = legal
    else:  # LETTER por defecto
        page_size = letter
    
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
        # Obtener ruta base desde configuración (por defecto escritorio)
        ruta_base = ajustes["salida"].get("ruta_base")
        
        # Si no existe o está vacía, usar escritorio
        if not ruta_base or ruta_base.strip() == "":
            ruta_base = obtener_ruta_escritorio_real()
            print(f"Usando escritorio por defecto: {ruta_base}")
        else:
            print(f"Usando ruta configurada: {ruta_base}")
        
        carpeta = ajustes["salida"]["carpeta"]
        nombre_pdf = ajustes["salida"]["nombre_pdf"]
        
        # Crear directorio completo
        directorio_salida = os.path.join(ruta_base, carpeta)
        os.makedirs(directorio_salida, exist_ok=True)
        nombre_archivo_salida = os.path.join(directorio_salida, nombre_pdf)
        
        print(f"Ruta completa del PDF: {nombre_archivo_salida}")

    # ===============================
    # GENERAR CÓDIGOS
    # ===============================
    diccionario_codigos_barras = {}
    errores = []
    advertencias = []
    
    for codigo_producto, _, precio_producto in lista_productos_con_cantidades:
        if codigo_producto not in diccionario_codigos_barras:
            try:
                if TIPO_CODIGO == "qr":
                    # Generar QR
                    nombre_archivo = f"codigo_qr_{codigo_producto}.png"
                    ruta = generar_codigo_qr(str(codigo_producto), nombre_archivo)
                    diccionario_codigos_barras[codigo_producto] = (ruta, precio_producto)
                    
                else:
                    # Validar código según tipo
                    codigo_valido = validar_codigo(codigo_producto, TIPO_CODIGO)
                    
                    if codigo_valido is None:
                        errores.append(f"Código '{codigo_producto}' inválido para {TIPO_CODIGO.upper()}")
                        continue
                    
                    # Advertir si se modificó el código
                    if str(codigo_valido) != str(codigo_producto):
                        advertencias.append(f"Código {codigo_producto} → {codigo_valido} (dígito de control añadido)")
                    
                    # Generar código de barras
                    generador = get_barcode_class(TIPO_CODIGO)
                    imagen = generador(str(codigo_valido), writer=ImageWriter())
                    opciones = {"write_text": MOSTRAR_TEXTO_CODIGO}
                    ruta = imagen.save(f"codigo_{TIPO_CODIGO}_{codigo_producto}", opciones)
                    diccionario_codigos_barras[codigo_producto] = (ruta, precio_producto)
                    
            except Exception as e:
                errores.append(f"Error generando código {codigo_producto}: {str(e)}")
                continue

    # Mostrar advertencias
    if advertencias:
        print("\nINFORMACIÓN:")
        for adv in advertencias:
            print(f"  {adv}")
        print()

    # Mostrar errores
    if errores:
        print("ERRORES:")
        for error in errores:
            print(f"  {error}")
        print()

    # Si no se generó ningún código, salir
    if not diccionario_codigos_barras:
        print("No se pudo generar ningún código válido. Verifique los datos.")
        return

    # ===============================
    # PDF
    # ===============================
    lienzo_pdf = canvas.Canvas(nombre_archivo_salida, pagesize=page_size)
    ancho_hoja, alto_hoja = page_size
    
    print(f"Tamaño de página: {pagesize_config} ({ancho_hoja/cm:.1f}cm x {alto_hoja/cm:.1f}cm)")

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

    codigos_generados = 0
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
                tamano_qr = min(ANCHO_CODIGO, ALTO_CODIGO)
                lienzo_pdf.drawImage(
                    ruta_img,
                    x_actual + (ANCHO_CODIGO - tamano_qr) / 2,
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

            codigos_generados += 1
            codigo_en_fila += 1
            if codigo_en_fila < CODIGOS_POR_FILA:
                x_actual += ANCHO_CODIGO + ESPACIO_HORIZONTAL
            else:
                x_actual = x_inicial
                y_actual -= altura_elemento + ESPACIO_VERTICAL
                codigo_en_fila = 0

    lienzo_pdf.save()
    print(f"\nPDF generado exitosamente: {nombre_archivo_salida}")
    print(f"Total de códigos en PDF: {codigos_generados}")

    # Limpiar archivos temporales
    archivos_eliminados = 0
    for codigo_producto, (ruta_archivo_temporal, _) in diccionario_codigos_barras.items():
        try:
            if os.path.exists(ruta_archivo_temporal):
                os.remove(ruta_archivo_temporal)
                archivos_eliminados += 1
        except Exception as e:
            print(f"Error eliminando archivo temporal {ruta_archivo_temporal}: {e}")
    
    print(f"Archivos temporales eliminados: {archivos_eliminados}\n")

