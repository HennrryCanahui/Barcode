import os
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from barcode import get_barcode_class
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

#import time

# Detecta correctamente el escritorio visible (OneDrive o local)
def obtener_escritorio_real():
    posibles_rutas = [
        os.path.join(os.path.expanduser("~"), "OneDrive", "Escritorio"),
        os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
        os.path.join(os.path.expanduser("~"), "Escritorio"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
    ]
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta
    return os.path.join(os.path.expanduser("~"), "Desktop")  # Fallback

# Lista de códigos y cantidades como tuplas
id_copias_list = []

#start = time.time()
def generar_codigos_barras_pdf(id_copias_list, output_filename=None):
    # Ruta por defecto: carpeta "codigos" en el escritorio visible
    if output_filename is None:
        desktop_path = obtener_escritorio_real()
        output_dir = os.path.join(desktop_path, "codigos")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, "codigos_barras.pdf")
    else:
        output_dir = os.path.dirname(output_filename)
        os.makedirs(output_dir, exist_ok=True)

    codigos_barras = {}
    for id, _, precio in id_copias_list:
        if id not in codigos_barras:
            CODE128 = get_barcode_class('code128')
            codigo_barra = CODE128(
                str(id),
                writer=ImageWriter()
            )
            filename = f"codigo_barra_{id}.png"
            options = {'write_text': False}  # Desactiva el número debajo del código de barras
            full_filename = codigo_barra.save(filename, options)
            codigos_barras[id] = (full_filename, precio)  # Guardar el archivo y el precio


    # Crear el PDF con los códigos de barras
    c = canvas.Canvas(output_filename, pagesize=letter)
    width, height = letter
    x = 0.5 * cm  # Margen izquierdo
    y = height - 0.8 * cm  # Margen superior

    barra_ancho = 3.5 * cm  # Ancho de cada código de barras
    barra_alto = 1 * cm  # Alto de cada código de barras

    codigos_por_fila = 6

    for id, cantidad, _ in id_copias_list:
        codigo_barra, precio = codigos_barras[id]
        for _ in range(cantidad):
            if os.path.exists(codigo_barra):
                # Precio a mostrar sobre el código de barras
                precio_texto = f"Q{precio}"  # Mostrar el precio ingresado por el usuario

                # Ajustar el tamaño y fuente para el precio
                c.setFont("Helvetica-Bold", 14)
                texto_ancho = c.stringWidth(precio_texto, "Helvetica-Bold", 14)

                # Calcular la posición X para centrar el texto respecto al código de barras
                texto_x = x + (barra_ancho - texto_ancho) / 2
                c.drawString(texto_x, y + 4, precio_texto)  # Dibujar el precio sobre el código de barras

                # Dibujar el código de barras
                c.drawImage(codigo_barra, x, y - barra_alto, width=barra_ancho, height=barra_alto)
                x += barra_ancho  # Mover la posición horizontal para el siguiente código de barras

                # Si ya se colocaron 6 códigos en la fila, saltar a la siguiente fila
                if (x + barra_ancho) > width:
                    x = 0.5 * cm  # Reiniciar al margen izquierdo
                    y -= barra_alto + 0.7 * cm  # Bajar a la siguiente fila

                # Verificar si es necesario crear una nueva página
                if y - barra_alto < 0.5 * cm:
                    c.showPage()
                    x = 0.5 * cm
                    y = height - 1.5 * cm
            else:
                print(f"Archivo no encontrado: {codigo_barra}")

    c.save()
    print(f"PDF generado: {output_filename}")

    # Eliminar archivos de imagen temporales
    for filename, _ in codigos_barras.values():
        try:
            if os.path.exists(filename):
                os.remove(filename)
            else:
                print(f"No se pudo encontrar el archivo para eliminar: {filename}")
        except Exception as e:
            print(f"No se pudo eliminar el archivo {filename}: {e}")

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



#   pip install pywin32
