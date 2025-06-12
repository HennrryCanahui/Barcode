import flet as ft
from Generador import generar_codigos_barras_pdf , obtener_escritorio_real
import functools
import random
import os
import subprocess
import platform


def main(page: ft.Page):
    page.title = "Generador de códigos de barras"
    
    # Configuración de la ventana
    page.window.width = 569
    page.window.height = 569
    page.window.min_width = 550
    page.window.min_height = 550
   # page.window_max_width = 1280
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK

    # Variables para almacenar datos
    codigos_list = []
    index_editar = None

    # Crear el SnackBar una sola vez
    snack_bar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snack_bar)

    # Función para mostrar mensajes de retroalimentación
    def mostrar_mensaje(mensaje, color=ft.Colors.GREEN):
        snack_bar.content = ft.Text(mensaje)
        snack_bar.bgcolor = color
        snack_bar.open = True
        page.update()

    # Función para generar un número aleatorio de 12 cifras
    def generar_numero_aleatorio(e):
        numero_aleatorio = str(random.randint(10**11, 10**12 - 1))  # Genera un número de 12 cifras
        txt_codigo.value = numero_aleatorio  # Asigna el número al campo de texto del código
        page.update()

    # Función para agregar o actualizar datos en la tabla
    def agregar_o_actualizar_datos(e):
        nonlocal index_editar
        codigo = txt_codigo.value.strip()
        cantidad = txt_cantidad.value.strip()
        precio = txt_precio.value.strip()

        if codigo and cantidad.isdigit() and precio.replace('.', '', 1).isdigit():
            if index_editar is not None:
                # Si estamos editando, actualizamos el registro en la lista
                codigos_list[index_editar] = {"codigo": codigo, "cantidad": int(cantidad), "precio": str(precio)}
                index_editar = None
                mostrar_mensaje("Registro actualizado correctamente.")
                
                # Cambiar el botón de vuelta a "Agregar"
                btn_agregar_actualizar.text = "Agregar"
                btn_agregar_actualizar.icon = ft.Icons.ADD
                btn_agregar_actualizar.bgcolor = ft.Colors.BLUE
            else:
                # Si no estamos editando, agregamos un nuevo registro
                codigos_list.append({"codigo": codigo, "cantidad": int(cantidad), "precio": str(precio)})
                mostrar_mensaje("Registro agregado correctamente.")
            
            actualizar_tabla()
            txt_codigo.value = txt_cantidad.value = txt_precio.value = ""
            txt_codigo.focus()
            page.update()
        else:
            mostrar_mensaje("Por favor, ingrese datos válidos.", ft.Colors.RED)

    # Función para actualizar la tabla
    def actualizar_tabla():
        tabla.rows.clear()
        for index, item in enumerate(codigos_list):
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["codigo"], color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(str(item["cantidad"]), color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(f"Q{item['precio']}", color=ft.Colors.BLACK)),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.EDIT, icon_color=ft.Colors.BLUE, 
                                                 on_click=functools.partial(editar_dato, index))),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED, 
                                                 on_click=functools.partial(eliminar_dato, index))),
                    ]
                )
            )
        page.update()

    # Función para editar datos
    def editar_dato(index, e):
        nonlocal index_editar
        item = codigos_list[index]
        index_editar = index
        txt_codigo.value = item["codigo"]
        txt_cantidad.value = str(item["cantidad"])
        txt_precio.value = item["precio"]

        # Cambiar el botón a modo "Actualizar"
        btn_agregar_actualizar.text = "Actualizar"
        btn_agregar_actualizar.icon = ft.Icons.UPDATE
        btn_agregar_actualizar.bgcolor = ft.Colors.INDIGO
        page.update()

    # Función para eliminar datos
    def eliminar_dato(index, e):
        nonlocal index_editar
        codigos_list.pop(index)
        
        # Si estábamos editando el elemento que se eliminó, resetear el botón
        if index_editar == index:
            index_editar = None
            btn_agregar_actualizar.text = "Agregar"
            btn_agregar_actualizar.icon = ft.Icons.ADD
            btn_agregar_actualizar.bgcolor = ft.Colors.BLUE
            txt_codigo.value = txt_cantidad.value = txt_precio.value = ""
        elif index_editar is not None and index_editar > index:
            # Ajustar el índice si eliminamos un elemento anterior al que estamos editando
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
        ruta = obtener_escritorio_real()
        ruta_pdf = os.path.expanduser(rf"{ruta}\codigos\codigos_barras.pdf")
        
        # Verificar si el archivo existe
        if not os.path.exists(ruta_pdf):
            mostrar_mensaje("No se encontró el archivo PDF. Genere el PDF primero.", ft.Colors.RED)
            return
        
        try:
            # Detectar el sistema operativo y abrir el archivo con el visor predeterminado
            sistema = platform.system()
            
            if sistema == "Windows":
                # En Windows, usar 'start' para abrir con el programa predeterminado
                os.startfile(ruta_pdf)
            elif sistema == "Darwin":  # macOS
                # En macOS, usar 'open'
                subprocess.run(["open", ruta_pdf])
            elif sistema == "Linux":
                # En Linux, usar 'xdg-open'
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

    # Botón combinado Agregar/Actualizar
    btn_agregar_actualizar = ft.ElevatedButton(
        "Agregar", 
        icon=ft.Icons.ADD, 
        on_click=agregar_o_actualizar_datos, 
        color=ft.Colors.WHITE, 
        bgcolor=ft.Colors.BLUE, 
        expand=True
    )
    
    btn_generar_pdf = ft.ElevatedButton("PDF", icon=ft.Icons.PICTURE_AS_PDF, on_click=enviar_a_pdf, 
                                      color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN, expand=True)
    
    # Botón para función futura (reemplaza al botón actualizar)
    btn_funcion_futura = ft.ElevatedButton("Función Futura", icon=ft.Icons.LIGHTBULB, 
                                         bgcolor=ft.Colors.GREY_400, disabled=True, color=ft.Colors.WHITE, expand=True)
    
    btn_ajustes = ft.ElevatedButton("Ajustes", icon=ft.Icons.SETTINGS, 
                                   color=ft.Colors.WHITE, bgcolor=ft.Colors.PURPLE, expand=True) 
    btn_imprimir = ft.ElevatedButton("Imprimir", icon=ft.Icons.LOCAL_PRINTSHOP, 
                                    on_click=imprimir_pdf, color=ft.Colors.WHITE, bgcolor=ft.Colors.TEAL, expand=True)

    # Tabla
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
            ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
            ft.DataColumn(ft.Text("Precio", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
            ft.DataColumn(ft.Text("Editar", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
            ft.DataColumn(ft.Text("Eliminar", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
        ],
        rows=[],
        border=ft.border.all(1, ft.Colors.BLUE),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.Colors.BLUE),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.BLUE),
    )

    # Layout principal
    page.add(
    ft.Column(
        controls=[
            # Encabezado con inputs y botones en ResponsiveRow
            ft.ResponsiveRow(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row([txt_codigo, txt_cantidad, txt_precio], spacing=10),
                        ],
                        col={"sm": 12, "md": 6},
                    ),
                    ft.Column(
                        controls=[
                            ft.Row([btn_agregar_actualizar, btn_generar_codigo, btn_generar_pdf], spacing=5),
                            ft.Row([btn_funcion_futura, btn_ajustes, btn_imprimir], spacing=5),
                        ],
                        col={"sm": 12, "md": 6},
                    ),
                ],
                spacing=10,
            ),
            ft.Divider(color=ft.Colors.BLUE),

            # Título centrado
            ft.Text(
                "Listado de códigos",
                style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                color=ft.Colors.BLUE,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),

            # Contenedor de la tabla centrado y expandible
            ft.Row(
                controls=[
                    ft.Container(
                        content=tabla,
                        padding=20,
                        border_radius=10,
                        bgcolor=ft.Colors.GREY_200,
                        expand=True,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
        ],
        expand=True,
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
)


if __name__ == "__main__":
    ft.app(target=main)


#  pyinstaller --onefile --noconsole Main.py
# flet run --web Main.py   ## run web
# flet run --android       ## android