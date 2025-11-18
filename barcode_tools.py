import os
import math
import tempfile
from barcode import get_barcode_class
from barcode.writer import ImageWriter
from PIL import Image
import qrcode


def _save_temp_png(image, filename_hint="img"):
    fd, path = tempfile.mkstemp(prefix=filename_hint, suffix=".png")
    os.close(fd)
    image.save(path)
    return path


def generar_code128_png(texto, tamaño_lado_cm=None):
    """Genera un PNG de Code128 y devuelve la ruta.

    `tamaño_lado_cm` se ignora para barcode: la escala se hará en el PDF.
    """
    code_class = get_barcode_class('code128')
    b = code_class(str(texto), writer=ImageWriter())
    # write_text False para no mostrar el número debajo
    try:
        ruta = b.save(f"codigo_barra_{texto}", {'write_text': False})
        # b.save devuelve la ruta sin extensión repetida en algunas versiones; asegurar .png
        if not ruta.lower().endswith('.png'):
            ruta = ruta + '.png'
        return ruta
    except Exception:
        # fallback: generar manualmente con Pillow si falla
        img = b.render(writer_options={'write_text': False})
        ruta = _save_temp_png(img, filename_hint=f"code128_{texto}")
        return ruta


def generar_qr_png(texto, tamaño_lado_cm=None, dpi=300):
    """Genera un PNG de QR y devuelve la ruta.

    `tamaño_lado_cm` se usa para ajustar el tamaño del PNG generado, aunque el
    escalado final lo hace el PDF.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(str(texto))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Si se especifica tamaño en cm, calcular píxeles aproximados
    if tamaño_lado_cm is not None:
        # dpi -> pixels per inch. 1 inch = 2.54 cm
        pixels = int((tamaño_lado_cm / 2.54) * dpi)
        img = img.resize((pixels, pixels), Image.NEAREST)

    ruta = _save_temp_png(img, filename_hint=f"qr_{texto}")
    return ruta
