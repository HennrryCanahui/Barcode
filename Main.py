import flet as ft
from Generador import generar_codigos_barras_pdf
import functools

def main(page: ft.Page):
    page.title = "Generador de códigos de barras"
    page.window.min_height = 600
    page.window.min_width = 1280
    page.window.max_width = 1280
    
    # Variables para almacenar datos
    codigos_list = []
    global index_editar  # Se declara global para que pueda ser usada en todas las funciones
    index_editar = None  # Inicialización de la variable global

    # Función para agregar datos a la tabla
    def agregar_datos(e):
        global index_editar  # Se debe declarar global aquí también
        codigo = txt_codigo.value.strip()
        cantidad = txt_cantidad.value.strip()
        precio = txt_precio.value.strip()

        if codigo and cantidad.isdigit() and precio.replace('.', '', 1).isdigit():
            if index_editar is not None:
                # Si estamos editando, actualizamos el registro en la lista
                codigos_list[index_editar] = {"codigo": codigo, "cantidad": int(cantidad), "precio": str(precio)}
                index_editar = None  # Reseteamos el índice de edición
            else:
                # Si no estamos editando, agregamos un nuevo registro
                codigos_list.append({"codigo": codigo, "cantidad": int(cantidad), "precio": str(precio)})
            
            actualizar_tabla()
            txt_codigo.value = txt_cantidad.value = txt_precio.value = ""
            txt_codigo.focus()
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, ingrese datos válidos"), bgcolor=ft.colors.RED)
            page.snack_bar.open()

    # Función para actualizar la tabla
    def actualizar_tabla():
        tabla.rows.clear()
        for index, item in enumerate(codigos_list):
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["codigo"])),

                        ft.DataCell(ft.Text(str(item["cantidad"]))),

                        ft.DataCell(ft.Text(f"Q{item['precio']}")),

                        # Usamos partial para pasar el index de manera correcta
                        ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, on_click=functools.partial(editar_dato, index))),

                        # Lo mismo con eliminar, pasamos el item
                        ft.DataCell(ft.IconButton(icon=ft.icons.DELETE, on_click=functools.partial(eliminar_dato, item))),
                    ]
                )
            )
        page.update()

    # Función para editar datos
    def editar_dato(index, e):
        global index_editar  # Se debe declarar global aquí también
        item = codigos_list[index]
        index_editar = index  # Guardamos el índice del registro que estamos editando
        txt_codigo.value = item["codigo"]
        txt_cantidad.value = str(item["cantidad"])
        txt_precio.value = item["precio"]

        # Actualizamos la tabla
        actualizar_tabla()

    # Función para eliminar datos
    def eliminar_dato(item, e):
        global index_editar  # Se debe declarar global aquí también
        codigos_list.remove(item)
        index_editar = None  # Reseteamos el índice de edición al eliminar un registro
        actualizar_tabla()

    # Función para enviar datos a la función generar_codigos_barras_pdf
    def enviar_a_pdf(e):
        if codigos_list:
            # Convertir lista en el formato necesario para la función
            id_copias_list = [(item["codigo"], item["cantidad"], item["precio"]) for item in codigos_list]
            generar_codigos_barras_pdf(id_copias_list)
        else:
            pass

    # Elementos de entrada
    txt_codigo = ft.TextField(label="Código", autofocus=True, expand=True)
    txt_cantidad = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER)
    txt_precio = ft.TextField(label="Precio (Q)", keyboard_type=ft.KeyboardType.NUMBER)

    # Botón para agregar datos
    btn_agregar = ft.ElevatedButton("Agregar", icon=ft.icons.ADD, on_click=agregar_datos)

    # Botón para generar PDF
    btn_generar_pdf = ft.ElevatedButton("Generar PDF", icon=ft.icons.PICTURE_AS_PDF, on_click=enviar_a_pdf)

    # Tabla editable
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Cantidad")),
            ft.DataColumn(ft.Text("Precio")),
            ft.DataColumn(ft.Text("Editar")),
            ft.DataColumn(ft.Text("Eliminar")),
        ],
        rows=[],
    )

    # Layout principal
    page.add(
        ft.Column(
            controls=[
                ft.Row([txt_codigo, txt_cantidad, txt_precio, btn_agregar, btn_generar_pdf], spacing=10),
                ft.Divider(),
                ft.Text("Listado de códigos", style="headlineMedium"),
                tabla,
            ],
            spacing=20,
        )
    )

# Ejecuta la aplicación
if __name__ == "__main__":
    ft.app(target=main)
