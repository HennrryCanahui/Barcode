import ctypes
from ctypes import wintypes


def obtener_ruta_escritorio_real():
    """Devuelve la ruta del escritorio del usuario en Windows.

    Función extraída de `Generador.py` para separar responsabilidades.
    """
    CSIDL_DESKTOP = 0
    SHGFP_TYPE_CURRENT = 0

    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf)

    return buf.value
