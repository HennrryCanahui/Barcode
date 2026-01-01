import flet as ft

def main(page: ft.Page):
    # Configuración de tema
    page.bgcolor = "#0f111a"
    page.theme_mode = ft.ThemeMode.DARK

    # --- LÓGICA DE LOS AJUSTES ---
    def guardar_ajustes(e):
        print(f"Puerto: {input_puerto.value}")
        dlg_ajustes.open = False
        page.update()

    def cerrar_ajustes(e):
        dlg_ajustes.open = False
        page.update()

    # --- UI DEL DIÁLOGO DE AJUSTES ---
    input_puerto = ft.TextField(
        label="Puerto de Impresora",
        border_color="purple"  # ← corregido
    )

    check_auto_gen = ft.Switch(
        label="Generar automáticamente",
        value=True
    )

    slider_densidad = ft.Slider(
        min=0,
        max=100,
        divisions=10,
        label="{value}%"  # ← así se usa el label
    )

    dlg_ajustes = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.SETTINGS, color="purple"),
            ft.Text("Configuración Avanzada")
        ]),
        content=ft.Column(
            [
                ft.Text("Personaliza el comportamiento del generador:"),
                input_puerto,
                check_auto_gen,
                slider_densidad,
            ],
            tight=True,
            spacing=20
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_ajustes),
            ft.ElevatedButton(
                "Guardar Cambios",
                bgcolor="purple",
                color="white",
                on_click=guardar_ajustes
            ),
        ],
    )

    # --- FUNCIÓN PARA MOSTRARLO ---
    def mostrar_ajustes(e):
        if dlg_ajustes not in page.overlay:
            page.overlay.append(dlg_ajustes)
        dlg_ajustes.open = True
        page.update()

    # Botón Ajustes
    btn_ajustes = ft.Container(
        content=ft.Row(
            [ft.Icon(ft.Icons.SETTINGS), ft.Text("Ajustes")],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor="#a020f0",
        padding=10,
        border_radius=20,
        expand=True,
        on_click=mostrar_ajustes
    )

    page.add(
        ft.Column(
            [
                ft.Text(
                    "Generador de códigos de barras",
                    size=30,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Row([btn_ajustes]),
            ],
            spacing=20
        )
    )

ft.app(target=main)
