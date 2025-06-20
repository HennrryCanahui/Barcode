import flet as ft

def main(page: ft.Page):
    contenedor = ft.Container(
        content=ft.Text("texto del contenido"),
        bgcolor=ft.Colors.AMBER,
        expand=True,
        margin=ft.margin.only(left=50, bottom=50)
    )

    page.add(contenedor)

ft.app(target=main)
