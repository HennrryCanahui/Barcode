import flet as ft
from Generador import generar_codigos_barras_pdf
import functools
import random  

def main(page: ft.Page):
    page.title = "Generador de códigos de barras"
    
    # Configuración de la ventana
    page.window_min_height = 600
    page.window_min_width = 1280
    page.window_max_width = 1280

    # Variables para almacenar datos
    codigos_list = []
    global index_editar
    index_editar = None

    # Función para mostrar mensajes de retroalimentación
    def mostrar_mensaje(mensaje, color=ft.colors.GREEN):
        page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor=color)
        page.snack_bar.open = True  
        page.update()

    # Función para generar un número aleatorio de 12 cifras
    def generar_numero_aleatorio(e):
        numero_aleatorio = str(random.randint(10**11, 10**12 - 1))  # Genera un número de 12 cifras
        txt_codigo.value = numero_aleatorio  # Asigna el número al campo de texto del código
        page.update()

    # Función para agregar o actualizar datos en la tabla
    def agregar_datos(e):
        global index_editar
        codigo = txt_codigo.value.strip()
        cantidad = txt_cantidad.value.strip()
        precio = txt_precio.value.strip()

        if codigo and cantidad.isdigit() and precio.replace('.', '', 1).isdigit():
            if index_editar is not None:
                # Si estamos editando, actualizamos el registro en la lista
                codigos_list[index_editar] = {"codigo": codigo, "cantidad": int(cantidad), "precio": str(precio)}
                index_editar = None
                mostrar_mensaje("Registro actualizado correctamente.")
            else:
                # Si no estamos editando, agregamos un nuevo registro
                codigos_list.append({"codigo": codigo, "cantidad": int(cantidad), "precio": str(precio)})
                mostrar_mensaje("Registro agregado correctamente.")
            
            actualizar_tabla()
            txt_codigo.value = txt_cantidad.value = txt_precio.value = ""
            txt_codigo.focus()

            # Deshabilitar el botón de actualizar
            btn_actualizar.disabled = True
            btn_actualizar.bgcolor = ft.colors.GREY_400  # Color del botón deshabilitado
            page.update()
        else:
            mostrar_mensaje("Por favor, ingrese datos válidos.", ft.colors.RED)

    # Función para actualizar la tabla
    def actualizar_tabla():
        tabla.rows.clear()
        for index, item in enumerate(codigos_list):
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["codigo"], color=ft.colors.BLACK)),  # Color del texto
                        ft.DataCell(ft.Text(str(item["cantidad"]), color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(f"Q{item['precio']}", color=ft.colors.BLACK)),
                        ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, icon_color=ft.colors.BLUE, on_click=functools.partial(editar_dato, index))),  # Color del ícono de editar
                        ft.DataCell(ft.IconButton(icon=ft.icons.DELETE, icon_color=ft.colors.RED, on_click=functools.partial(eliminar_dato, item))),  # Color del ícono de eliminar
                    ]
                )
            )
        page.update()

    # Función para editar datos
    def editar_dato(index, e):
        global index_editar
        item = codigos_list[index]
        index_editar = index
        txt_codigo.value = item["codigo"]
        txt_cantidad.value = str(item["cantidad"])
        txt_precio.value = item["precio"]

        # Habilitar el botón de actualizar
        btn_actualizar.disabled = False
        btn_actualizar.bgcolor = ft.colors.BLUE  # Color del botón habilitado
        page.update()

    # Función para eliminar datos
    def eliminar_dato(item, e):
        global index_editar
        codigos_list.remove(item)
        index_editar = None
        actualizar_tabla()
        mostrar_mensaje("Registro eliminado correctamente.")

    # Función para enviar datos a la función generar_codigos_barras_pdf
    def enviar_a_pdf(e):
        if codigos_list:
            id_copias_list = [(item["codigo"], item["cantidad"], item["precio"]) for item in codigos_list]
            generar_codigos_barras_pdf(id_copias_list)
            mostrar_mensaje("PDF generado correctamente.")
        else:
            mostrar_mensaje("La lista está vacía. Agregue elementos antes de generar el PDF.", ft.colors.RED)

    # Elementos de entrada
    txt_codigo = ft.TextField(label="Código", autofocus=True, expand=True, border_color=ft.colors.BLUE)  # Color del borde
    txt_cantidad = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER, expand=True, border_color=ft.colors.BLUE)
    txt_precio = ft.TextField(label="Precio (Q)", keyboard_type=ft.KeyboardType.NUMBER, expand=True, border_color=ft.colors.BLUE)

    # Botón para generar un número aleatorio de 12 cifras
    btn_generar_codigo = ft.ElevatedButton(
        "Generar Código",
        icon=ft.icons.CASINO,  # Ícono de un dado (puedes cambiarlo)
        on_click=generar_numero_aleatorio,
        color=ft.colors.WHITE,
        bgcolor=ft.colors.ORANGE,  # Color del botón
    )

    # Botón para agregar datos
    btn_agregar = ft.ElevatedButton("Agregar", icon=ft.icons.ADD, on_click=agregar_datos, color=ft.colors.WHITE, bgcolor=ft.colors.BLUE)  # Color del botón

    # Botón para generar PDF
    btn_generar_pdf = ft.ElevatedButton("Generar PDF", icon=ft.icons.PICTURE_AS_PDF, on_click=enviar_a_pdf, color=ft.colors.WHITE, bgcolor=ft.colors.GREEN)  # Color del botón

    # Botón para actualizar datos
    btn_actualizar = ft.ElevatedButton("Actualizar", icon=ft.icons.UPDATE, on_click=agregar_datos, bgcolor=ft.colors.GREY_400, disabled=True, color=ft.colors.WHITE)  # Color del botón deshabilitado

    
    Ajustes = ft.ElevatedButton("Ajustes", icon=ft.icons.SETTINGS, color=ft.colors.WHITE, bgcolor=ft.colors.PURPLE) 
    Imprimir_pdf = ft.ElevatedButton("Imprimir PDF", icon=ft.icons.LOCAL_PRINTSHOP, color=ft.colors.WHITE, bgcolor=ft.colors.TEAL)

    # Tabla editable
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código", weight=ft.FontWeight.BOLD, color=ft.colors.BLACK)),  # Color del texto del encabezado
            ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD, color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Precio", weight=ft.FontWeight.BOLD, color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Editar", weight=ft.FontWeight.BOLD, color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Eliminar", weight=ft.FontWeight.BOLD, color=ft.colors.BLACK)),
        ],
        rows=[],
        border=ft.border.all(1, ft.colors.BLUE),  # Color del borde de la tabla
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE),  # Color de las líneas verticales
        horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE),  # Color de las líneas horizontales
    )

    # Layout principal
        # Layout principal
    page.add(
        ft.Row(
            controls=[
                # Lado izquierdo: Campos de entrada en una sola fila horizontal
                ft.Column(
                    controls=[
                        ft.Row([txt_codigo, txt_cantidad, txt_precio], spacing=10, alignment=ft.MainAxisAlignment.START),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                ),
                # Lado derecho: Botones en una matriz 2x3
                ft.Column(
                    controls=[
                        ft.Row([btn_agregar, btn_generar_codigo, btn_generar_pdf], spacing=10),
                        ft.Row([btn_actualizar, Ajustes, Imprimir_pdf], spacing=10),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=20,
            expand=False,
        ),
        ft.Divider(color=ft.colors.BLUE),  # Color del divisor

        # Contenedor para el listado de códigos (centrado)
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Listado de códigos", style="headlineMedium", color=ft.colors.BLUE, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(tabla, padding=20, border_radius=10, bgcolor=ft.colors.GREY_200),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.center,
        ),
    )

# Ejecuta la aplicación
if __name__ == "__main__":
    ft.app(target=main)
