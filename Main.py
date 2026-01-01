import flet as ft
from Generador import generar_codigos_barras_pdf, obtener_ruta_escritorio_real
import functools
import random
import os
import subprocess
import platform
import json

def main(page: ft.Page):
    page.title = "Generador de códigos de barras"
    
    # Configuración de la ventana
    page.window.width = 657
    page.window.height = 700
    page.window.min_width = 657
    page.window.min_height = 700
  
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK

    # Variables para almacenar datos
    codigos_list = []
    index_editar = None

    # Crear el SnackBar una sola vez
    snack_bar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snack_bar)

    
    def cargar_ajustes(ruta="ajustes.json"):
        # Si no existe el archivo, crear uno con valores por defecto
        if not os.path.exists(ruta):
            ajustes_default = {
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
                    "tipo": "code128",
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
                    "nombre_pdf": "codigos_barras.pdf"
                }
            }
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(ajustes_default, f, indent=4, ensure_ascii=False)
            return ajustes_default

        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    def guardar_ajustes(ajustes, ruta="ajustes.json"):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(ajustes, f, indent=4, ensure_ascii=False)

    # --- DIÁLOGO DE AJUSTES ---
    def mostrar_ajustes(e):
        ajustes = cargar_ajustes()

        # ===== CAMPOS PDF =====
        dropdown_pagesize = ft.Dropdown(
            label="Tamaño de página",
            value=ajustes["pdf"]["pagesize"],
            options=[
                ft.dropdown.Option("LETTER"),
                ft.dropdown.Option("A4"),
                ft.dropdown.Option("LEGAL"),
            ],
            border_color=ft.Colors.PURPLE,
            expand=True
        )

        input_margen_sup = ft.TextField(
            label="Margen Superior (cm)",
            value=str(ajustes["pdf"]["margenes"]["superior_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.PURPLE,
            expand=True
        )

        input_margen_inf = ft.TextField(
            label="Margen Inferior (cm)",
            value=str(ajustes["pdf"]["margenes"]["inferior_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.PURPLE,
            expand=True
        )

        input_margen_izq = ft.TextField(
            label="Margen Izquierdo (cm)",
            value=str(ajustes["pdf"]["margenes"]["izquierdo_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.PURPLE,
            expand=True
        )

        input_margen_der = ft.TextField(
            label="Margen Derecho (cm)",
            value=str(ajustes["pdf"]["margenes"]["derecho_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.PURPLE,
            expand=True
        )

        # ===== CAMPOS CÓDIGO DE BARRAS =====
        input_ancho_codigo = ft.TextField(
            label="Ancho código (cm)",
            value=str(ajustes["codigo_barras"]["ancho_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.BLUE,
            expand=True
        )

        input_alto_codigo = ft.TextField(
            label="Alto código (cm)",
            value=str(ajustes["codigo_barras"]["alto_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.BLUE,
            expand=True
        )

        switch_mostrar_texto = ft.Switch(
            label="Mostrar texto bajo el código",
            value=ajustes["codigo_barras"]["mostrar_texto"],
            expand=True
        )

        # ===== CAMPOS GRILLA =====
        input_codigos_fila = ft.TextField(
            label="Códigos por fila",
            value=str(ajustes["grilla"]["codigos_por_fila"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREEN,
            expand=True
        )

        input_espacio_h = ft.TextField(
            label="Espacio horizontal (cm)",
            value=str(ajustes["grilla"]["espacio_horizontal_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREEN,
            expand=True
        )

        input_espacio_v = ft.TextField(
            label="Espacio vertical (cm)",
            value=str(ajustes["grilla"]["espacio_vertical_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREEN,
            expand=True
        )

        input_espacio_precio = ft.TextField(
            label="Espacio precio (cm)",
            value=str(ajustes["grilla"]["espacio_precio_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.GREEN,
            expand=True
        )

        # ===== CAMPOS PRECIO =====
        input_prefijo_precio = ft.TextField(
            label="Prefijo precio",
            value=ajustes["precio"]["prefijo"],
            border_color=ft.Colors.ORANGE,
            expand=True
        )

        input_tamano_fuente = ft.TextField(
            label="Tamaño fuente precio",
            value=str(ajustes["precio"]["tamano"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.ORANGE,
            expand=True
        )

        input_offset_y = ft.TextField(
            label="Offset Y precio (cm)",
            value=str(ajustes["precio"]["offset_y_cm"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.ORANGE,
            expand=True
        )

        dropdown_fuente = ft.Dropdown(
            label="Fuente precio",
            value=ajustes["precio"]["fuente"],
            options=[
                ft.dropdown.Option("Helvetica"),
                ft.dropdown.Option("Helvetica-Bold"),
                ft.dropdown.Option("Times-Roman"),
                ft.dropdown.Option("Times-Bold"),
                ft.dropdown.Option("Courier"),
                ft.dropdown.Option("Courier-Bold"),
            ],
            border_color=ft.Colors.ORANGE,
            expand=True
        )

        # ===== CAMPOS SALIDA =====
        input_carpeta = ft.TextField(
            label="Carpeta de salida",
            value=ajustes["salida"]["carpeta"],
            border_color=ft.Colors.TEAL,
            expand=True
        )

        input_nombre_pdf = ft.TextField(
            label="Nombre del PDF",
            value=ajustes["salida"]["nombre_pdf"],
            border_color=ft.Colors.TEAL,
            expand=True
        )

        def guardar_y_cerrar(e):
            try:
                # Actualizar valores en el diccionario
                ajustes["pdf"]["pagesize"] = dropdown_pagesize.value
                ajustes["pdf"]["margenes"]["superior_cm"] = float(input_margen_sup.value)
                ajustes["pdf"]["margenes"]["inferior_cm"] = float(input_margen_inf.value)
                ajustes["pdf"]["margenes"]["izquierdo_cm"] = float(input_margen_izq.value)
                ajustes["pdf"]["margenes"]["derecho_cm"] = float(input_margen_der.value)
                
                ajustes["codigo_barras"]["ancho_cm"] = float(input_ancho_codigo.value)
                ajustes["codigo_barras"]["alto_cm"] = float(input_alto_codigo.value)
                ajustes["codigo_barras"]["mostrar_texto"] = switch_mostrar_texto.value
                
                ajustes["grilla"]["codigos_por_fila"] = int(input_codigos_fila.value)
                ajustes["grilla"]["espacio_horizontal_cm"] = float(input_espacio_h.value)
                ajustes["grilla"]["espacio_vertical_cm"] = float(input_espacio_v.value)
                ajustes["grilla"]["espacio_precio_cm"] = float(input_espacio_precio.value)
                
                ajustes["precio"]["fuente"] = dropdown_fuente.value
                ajustes["precio"]["tamano"] = int(input_tamano_fuente.value)
                ajustes["precio"]["prefijo"] = input_prefijo_precio.value
                ajustes["precio"]["offset_y_cm"] = float(input_offset_y.value)
                
                ajustes["salida"]["carpeta"] = input_carpeta.value
                ajustes["salida"]["nombre_pdf"] = input_nombre_pdf.value
                
                # Guardar en archivo
                guardar_ajustes(ajustes)
                mostrar_mensaje("✓ Ajustes guardados correctamente", ft.Colors.GREEN)
                dlg_ajustes.open = False
                page.update()
                
            except ValueError as ex:
                mostrar_mensaje(f"Error: Ingrese valores numéricos válidos - {str(ex)}", ft.Colors.RED)
            except Exception as ex:
                mostrar_mensaje(f"Error al guardar: {str(ex)}", ft.Colors.RED)

        def cerrar_sin_guardar(e):
            dlg_ajustes.open = False
            page.update()

        # ===== CREAR DIÁLOGO =====
        dlg_ajustes = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.PURPLE),
                ft.Text("Configuración de Impresión", weight=ft.FontWeight.BOLD, size=18)
            ]),
            content=ft.Container(
                content=ft.Column(
                    [
                        # Sección PDF
                        ft.Row([
                            ft.Icon(ft.Icons.PICTURE_AS_PDF, color=ft.Colors.PURPLE, size=18),
                            ft.Text("PDF", weight=ft.FontWeight.BOLD, size=15)
                        ]),
                        ft.Container(
                            content=dropdown_pagesize,
                            padding=ft.padding.only(bottom=5)
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    input_margen_sup,
                                    input_margen_inf
                                ],
                                spacing=8
                            ),
                            padding=ft.padding.only(bottom=5)
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    input_margen_izq,
                                    input_margen_der
                                ],
                                spacing=8
                            ),
                            padding=ft.padding.only(bottom=5)
                        ),

                        ft.Divider(height=15, color=ft.Colors.GREY_700),

                        # Sección Código de Barras
                        ft.Row([
                            ft.Icon(ft.Icons.QR_CODE, color=ft.Colors.BLUE, size=18),
                            ft.Text("Código de Barras", weight=ft.FontWeight.BOLD, size=15)
                        ]),
                        ft.Container(
                            content=ft.Row(
                                [
                                    input_ancho_codigo,
                                    input_alto_codigo
                                ],
                                spacing=8
                            ),
                            padding=ft.padding.only(bottom=5)
                        ),
                        ft.Container(
                            content=switch_mostrar_texto,
                            padding=ft.padding.only(bottom=5)
                        ),

                        ft.Divider(height=15, color=ft.Colors.GREY_700),

                        # Sección Grilla
                        ft.Row([
                            ft.Icon(ft.Icons.GRID_ON, color=ft.Colors.GREEN, size=18),
                            ft.Text("Grilla", weight=ft.FontWeight.BOLD, size=15)
                        ]),
                        ft.Container(
                            content=input_codigos_fila,
                            padding=ft.padding.only(bottom=5)
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    input_espacio_h,
                                    input_espacio_v
                                ],
                                spacing=8
                            ),
                            padding=ft.padding.only(bottom=5)
                        ),
                        ft.Container(
                            content=input_espacio_precio,
                            padding=ft.padding.only(bottom=5)
                        ),

                        ft.Divider(height=15, color=ft.Colors.GREY_700),

                        # Sección Precio
                        ft.Row([
                            ft.Icon(ft.Icons.ATTACH_MONEY, color=ft.Colors.ORANGE, size=18),
                            ft.Text("Precio", weight=ft.FontWeight.BOLD, size=15)
                        ]),
                        ft.Container(
                            content=dropdown_fuente,
                            padding=ft.padding.only(bottom=5)
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    input_prefijo_precio,
                                    input_tamano_fuente
                                ],
                                spacing=8
                            ),
                            padding=ft.padding.only(bottom=5)
                        ),
                        ft.Container(
                            content=input_offset_y,
                            padding=ft.padding.only(bottom=5)
                        ),

                        ft.Divider(height=15, color=ft.Colors.GREY_700),

                        # Sección Salida
                        ft.Row([
                            ft.Icon(ft.Icons.FOLDER, color=ft.Colors.TEAL, size=18),
                            ft.Text("Salida", weight=ft.FontWeight.BOLD, size=15)
                        ]),
                        ft.Container(
                            content=input_carpeta,
                            padding=ft.padding.only(bottom=5)
                        ),
                        ft.Container(
                            content=input_nombre_pdf,
                            padding=ft.padding.only(bottom=5)
                        ),
                    ],
                    spacing=8,
                    scroll=ft.ScrollMode.HIDDEN
                ),
                width=500,
                height=500,
                padding=ft.padding.all(12)
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=cerrar_sin_guardar
                ),
                ft.ElevatedButton(
                    "Guardar Cambios",
                    icon=ft.Icons.SAVE,
                    bgcolor=ft.Colors.PURPLE,
                    color=ft.Colors.WHITE,
                    on_click=guardar_y_cerrar
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Agregar el diálogo al overlay y abrirlo
        if dlg_ajustes not in page.overlay:
            page.overlay.append(dlg_ajustes)
        dlg_ajustes.open = True
        page.update()

    # Función para mostrar mensajes de retroalimentación
    def mostrar_mensaje(mensaje, color=ft.Colors.GREEN):
        snack_bar.content = ft.Text(mensaje)
        snack_bar.bgcolor = color
        snack_bar.open = True
        page.update()

    # Función para generar un número aleatorio de 12 cifras
    def generar_numero_aleatorio(e):
        numero_aleatorio = str(random.randint(10**11, 10**12 - 1))
        txt_codigo.value = numero_aleatorio
        page.update()

    # Función para agregar o actualizar datos en la tabla
    def agregar_o_actualizar_datos(e):
        nonlocal index_editar
        codigo = txt_codigo.value.strip()
        cantidad = txt_cantidad.value.strip()
        precio = txt_precio.value.strip()

        if codigo and cantidad.isdigit() and precio.replace('.', '', 1).isdigit():
            if index_editar is not None:
                codigos_list[index_editar] = {"codigo": codigo, "cantidad": int(cantidad), "precio": str(precio)}
                index_editar = None
                mostrar_mensaje("Registro actualizado correctamente.")
                
                btn_agregar_actualizar.text = "Agregar"
                btn_agregar_actualizar.icon = ft.Icons.ADD
                btn_agregar_actualizar.bgcolor = ft.Colors.BLUE
            else:
                codigos_list.append({"codigo": codigo, "cantidad": int(cantidad), "precio": str(precio)})
                mostrar_mensaje("Registro agregado correctamente.")
            
            actualizar_tabla()
            txt_codigo.value = txt_cantidad.value = txt_precio.value = ""
            txt_codigo.focus()
            page.update()
        else:
            mostrar_mensaje("Por favor, ingrese datos válidos.", ft.Colors.RED)

    # Función para editar datos
    def editar_dato(index, e):
        nonlocal index_editar
        item = codigos_list[index]
        index_editar = index
        txt_codigo.value = item["codigo"]
        txt_cantidad.value = str(item["cantidad"])
        txt_precio.value = item["precio"]

        btn_agregar_actualizar.text = "Actualizar"
        btn_agregar_actualizar.icon = ft.Icons.UPDATE
        btn_agregar_actualizar.bgcolor = ft.Colors.INDIGO
        page.update()

    # Función para eliminar datos
    def eliminar_dato(index, e):
        nonlocal index_editar
        codigos_list.pop(index)
        
        if index_editar == index:
            index_editar = None
            btn_agregar_actualizar.text = "Agregar"
            btn_agregar_actualizar.icon = ft.Icons.ADD
            btn_agregar_actualizar.bgcolor = ft.Colors.BLUE
            txt_codigo.value = txt_cantidad.value = txt_precio.value = ""
        elif index_editar is not None and index_editar > index:
            index_editar -= 1
            
        actualizar_tabla()
        mostrar_mensaje("Registro eliminado correctamente.")

    # Función para enviar datos a la función generar_codigos_barras_pdf
    def enviar_a_pdf(e):
        if codigos_list:
            id_copias_list = [(item["codigo"], item["cantidad"], item["precio"]) for item in codigos_list]
            generar_codigos_barras_pdf(id_copias_list)
            mostrar_mensaje("PDF generado correctamente.")
        else:
            mostrar_mensaje("La lista está vacía. Agregue elementos antes de generar el PDF.", ft.Colors.RED)

    # Función para imprimir
    def imprimir_pdf(e):
        ruta = obtener_ruta_escritorio_real()
        ruta_pdf = os.path.expanduser(rf"{ruta}\codigos\codigos_barras.pdf")
        
        if not os.path.exists(ruta_pdf):
            mostrar_mensaje("No se encontró el archivo PDF. Genere el PDF primero.", ft.Colors.RED)
            return
        
        try:
            sistema = platform.system()
            
            if sistema == "Windows":
                os.startfile(ruta_pdf)
            elif sistema == "Darwin":
                subprocess.run(["open", ruta_pdf])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", ruta_pdf])
            else:
                mostrar_mensaje("Sistema operativo no soportado para abrir archivos.", ft.Colors.RED)
                return
                
            mostrar_mensaje("Abriendo archivo PDF para imprimir...")
            
        except Exception as ex:
            mostrar_mensaje(f"Error al abrir el archivo: {str(ex)}", ft.Colors.RED)

    # Elementos de entrada
    txt_codigo = ft.TextField(label="Código", autofocus=True, expand=True, border_color=ft.Colors.BLUE)
    txt_cantidad = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER, expand=True, border_color=ft.Colors.BLUE)
    txt_precio = ft.TextField(label="Precio (Q)", keyboard_type=ft.KeyboardType.NUMBER, expand=True, border_color=ft.Colors.BLUE)

    # Botones
    btn_generar_codigo = ft.ElevatedButton(
        "Generar",
        icon=ft.Icons.CASINO,
        on_click=generar_numero_aleatorio,
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.ORANGE,
        expand=True,
    )

    btn_agregar_actualizar = ft.ElevatedButton(
        "Agregar", 
        icon=ft.Icons.ADD, 
        on_click=agregar_o_actualizar_datos, 
        color=ft.Colors.WHITE, 
        bgcolor=ft.Colors.BLUE, 
        expand=True
    )
    
    btn_generar_pdf = ft.ElevatedButton(
        "PDF", 
        icon=ft.Icons.PICTURE_AS_PDF, 
        on_click=enviar_a_pdf, 
        color=ft.Colors.WHITE, 
        bgcolor=ft.Colors.GREEN, 
        expand=True
    )
    
    btn_funcion_futura = ft.ElevatedButton(
        "Función Futura", 
        icon=ft.Icons.LIGHTBULB, 
        bgcolor=ft.Colors.GREY_400, 
        disabled=True, 
        color=ft.Colors.WHITE, 
        expand=True
    )
    
    btn_ajustes = ft.ElevatedButton(
        "Ajustes", 
        icon=ft.Icons.SETTINGS, 
        color=ft.Colors.WHITE, 
        bgcolor=ft.Colors.PURPLE, 
        expand=True, 
        on_click=mostrar_ajustes
    ) 
    
    btn_imprimir = ft.ElevatedButton(
        "Imprimir", 
        icon=ft.Icons.LOCAL_PRINTSHOP, 
        on_click=imprimir_pdf, 
        color=ft.Colors.WHITE, 
        bgcolor=ft.Colors.TEAL, 
        expand=True
    )

    tamaño_texto = 17

    def actualizar_tabla():
        lista_contenido = container_tabla.content.controls[1].content
        lista_contenido.controls.clear()

        for index, item in enumerate(codigos_list):
            fila = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                item["codigo"], 
                                color=ft.Colors.WHITE, 
                                size=17, 
                                text_align=ft.TextAlign.CENTER,
                                selectable=True
                            ),
                            padding=ft.padding.symmetric(horizontal=8, vertical=8),
                            alignment=ft.alignment.center,
                            expand=4,
                        ),
                        ft.Container(
                            content=ft.Text(
                                str(item["cantidad"]), 
                                color=ft.Colors.WHITE, 
                                size=17,
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=ft.padding.symmetric(horizontal=8, vertical=8),
                            alignment=ft.alignment.center,
                            expand=2,
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"Q{item['precio']}", 
                                color=ft.Colors.WHITE, 
                                size=17,
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=ft.padding.symmetric(horizontal=8, vertical=8),
                            alignment=ft.alignment.center,
                            expand=3,
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT, 
                                        icon_color=ft.Colors.BLUE, 
                                        icon_size=20,
                                        on_click=functools.partial(editar_dato, index),
                                        tooltip="Editar"
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE, 
                                        icon_color=ft.Colors.RED, 
                                        icon_size=20,
                                        on_click=functools.partial(eliminar_dato, index),
                                        tooltip="Eliminar"
                                    ),
                                ],
                                spacing=0,
                                tight=True,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            alignment=ft.alignment.center,
                            expand=3,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
                bgcolor=ft.Colors.GREY_900,
                border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.BLUE_GREY_700)),
                padding=ft.padding.all(0),
                border_radius=ft.border_radius.all(5),
                expand=True,
            )
            lista_contenido.controls.append(fila)
        
        page.update()

    container_tabla = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    "Código", 
                                    weight=ft.FontWeight.BOLD, 
                                    size=tamaño_texto, 
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                expand=4,
                                alignment=ft.alignment.center,
                                padding=ft.padding.symmetric(horizontal=8, vertical=8),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "Cantidad", 
                                    weight=ft.FontWeight.BOLD, 
                                    size=tamaño_texto, 
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                expand=2,
                                padding=ft.padding.symmetric(horizontal=8, vertical=8),
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "Precio", 
                                    weight=ft.FontWeight.BOLD, 
                                    size=tamaño_texto, 
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                expand=3,
                                padding=ft.padding.symmetric(horizontal=8, vertical=8),
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "Acción", 
                                    weight=ft.FontWeight.BOLD, 
                                    size=tamaño_texto, 
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                expand=3,
                                padding=ft.padding.symmetric(horizontal=8, vertical=8),
                                alignment=ft.alignment.center,
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    bgcolor=ft.Colors.BLUE_GREY_900,
                    border=ft.border.all(1, ft.Colors.BLUE),
                    border_radius=ft.border_radius.only(top_left=10, top_right=10),
                    expand=False,
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=[],
                        height=294,
                        spacing=0,
                        padding=ft.padding.all(0),
                        expand=True,
                    ),
                    border=ft.border.only(
                        left=ft.border.BorderSide(1, ft.Colors.BLUE),
                        right=ft.border.BorderSide(1, ft.Colors.BLUE),
                        bottom=ft.border.BorderSide(1, ft.Colors.BLUE),
                    ),
                    border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                    bgcolor=ft.Colors.GREY_800,
                    expand=True,
                )
            ],
            spacing=0,
            expand=True,
        ),
        margin=ft.margin.only(left=30, right=30, top=10, bottom=30),
        expand=True,
    )

    page.add(
        ft.Column(
            controls=[
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Row([txt_codigo, txt_cantidad, txt_precio], spacing=10),
                            ],
                            col={"sm": 12, "md": 7},
                        ),
                        ft.Column(
                            controls=[
                                ft.Row([btn_agregar_actualizar, btn_generar_codigo, btn_generar_pdf], spacing=5),
                                ft.Row([btn_ajustes, btn_imprimir], spacing=5),
                            ],
                            col={"sm": 12, "md": 5},
                        ),
                    ],
                    spacing=10,
                ),
                ft.Divider(color=ft.Colors.BLUE),

                ft.Row(
                    controls=[
                        ft.Text(
                            "Listado de códigos",
                            style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                            color=ft.Colors.BLUE,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                container_tabla,
            ],
            expand=True,
            spacing=20,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)