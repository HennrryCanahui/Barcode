from Generador import generar_codigos_barras_pdf

# Lista de ejemplo: (codigo, cantidad, precio)
lista = [
    ("Q69", 6, "69"),
    ("123456789012", 6, "25"),
]

# Generar PDF de prueba con QR
generar_codigos_barras_pdf(lista, nombre_archivo_salida=None, formato='qr')

# Generar PDF de prueba con código de barras (descomenta para probar)
# generar_codigos_barras_pdf(lista, nombre_archivo_salida=None, formato='barcode')
