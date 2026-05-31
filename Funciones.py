import os
import json
import random

def obtener_ruta_escritorio_real():
    import ctypes
    from ctypes import wintypes

    CSIDL_DESKTOP = 0
    SHGFP_TYPE_CURRENT = 0

    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(
        None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf
    )
    return buf.value


def obtener_valores_por_defecto():
    return {
        "pdf": {
            "pagesize": "LETTER",
            "margenes": {
                "superior_cm": 0.7,
                "inferior_cm": 0.5,
                "izquierdo_cm": 0.2,
                "derecho_cm": 0.2
            }
        },
        "codigo_barras": {
            "tipo": "CODE128",
            "ancho_cm": 3.3,
            "alto_cm": 1.0,
            "mostrar_texto": False
        },
        "grilla": {
            "codigos_por_fila": 6,
            "espacio_horizontal_cm": 0.15,
            "espacio_vertical_cm": 0.15,
            "espacio_precio_cm": 0.25
        },
        "precio": {
            "fuente": "Helvetica-Bold",
            "tamano": 14,
            "prefijo": "Q",
            "offset_y_cm": 0.4
        },
        "salida": {
            "carpeta": "codigos",
            "nombre_pdf": "codigos_barras.pdf",
            "ruta_base": obtener_ruta_escritorio_real(),
            "eliminar_lista_al_crear_pdf": True
        }
    }


def cargar_ajustes(ruta="ajustes.json"):
    if not os.path.exists(ruta):
        ajustes_default = obtener_valores_por_defecto()
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(ajustes_default, f, indent=4, ensure_ascii=False)
        return ajustes_default

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)



# Funciones de ajustes 

def guardar_ajustes(ajustes, ruta="ajustes.json"):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(ajustes, f, indent=4, ensure_ascii=False)



def generador_codigo():
    ajustes = cargar_ajustes()
    tipo_codigo = ajustes["codigo_barras"]["tipo"].upper()

    match tipo_codigo:
        case "CODE128":
            return ''.join([str(random.randint(0, 9)) for _ in range(12)])
        case "EAN13":
            return ''.join([str(random.randint(0, 9)) for _ in range(12)])
        case "EAN8":
            return ''.join([str(random.randint(0, 9)) for _ in range(8)])
        case "UPCA":
            return ''.join([str(random.randint(0, 9)) for _ in range(12)])
        case "CODE39":
            caracteres = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            return ''.join([random.choice(caracteres) for _ in range(10)])
        case "CODE93":
            caracteres = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            return ''.join([random.choice(caracteres) for _ in range(10)])
        case "ITF":
            return ''.join([str(random.randint(0, 9)) for _ in range(12)])
        case "QR":
            return ''.join([str(random.randint(0, 9)) for _ in range(12)])  
        case _:
            return ''.join([str(random.randint(0, 9)) for _ in range(12)])  



