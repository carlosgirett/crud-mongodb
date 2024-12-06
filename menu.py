import flet as ft
from conexion.conexion import MongoDBConnection  # Importa la clase de conexión
from vistas.usuarios_view import mostrar_usuarios_view  # Importa la vista de usuarios

def main(page: ft.Page):
    page.title = "Barra de Navegación"

    # Crear la conexión a MongoDB
    db = MongoDBConnection()

    # Contenedor para mostrar contenido dinámico
    content = ft.Column(
        [],
        alignment=ft.MainAxisAlignment.START,  # Alineación hacia arriba
        expand=True,
        scroll="auto"
    )

    # Inicialización de la tabla para usuarios (se reutiliza en la vista de usuarios)
    users_table = ft.DataTable(
        border=ft.border.all(1, "grey"),
        border_radius=10,
        vertical_lines=ft.BorderSide(1, "grey"),
        width=1000,
        columns=[
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Clave")),
            ft.DataColumn(ft.Text("E-mail")),
            ft.DataColumn(ft.Text("Rol")),
            ft.DataColumn(ft.Text("Estado")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
    )

    # Función para cambiar el contenido según la opción seleccionada
    def on_navigation_change(e=None):
        selected_index = rail.selected_index  # Lee el índice seleccionado del NavigationRail
        content.controls.clear()  # Limpia el contenido previo

        if selected_index == 0:  # Opción "Usuarios"
            mostrar_usuarios_view(page, content, db, users_table)  # Pasa la tabla aquí
        elif selected_index == 1:  # Opción "Configuración"
            content.controls.append(
                ft.Column(
                    [ft.Text("Opción 2 seleccionada: Configuración", size=24, weight="bold")],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                )
            )
        elif selected_index == 2:  # Opción "Ayuda"
            content.controls.append(
                ft.Column(
                    [ft.Text("Opción 3 seleccionada: Ayuda", size=24, weight="bold")],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                )
            )

        page.update()

    # NavigationRail
    rail = ft.NavigationRail(
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        selected_index=0,  # Elemento predeterminado
        on_change=on_navigation_change,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.PERSON),
                selected_icon=ft.Icon(ft.Icons.PERSON),
                label="Usuarios",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.SETTINGS),
                selected_icon=ft.Icon(ft.Icons.SETTINGS),
                label="Configuración",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.HELP),
                selected_icon=ft.Icon(ft.Icons.HELP),
                label="Ayuda",
            ),
        ],
    )

    # Layout principal que contiene el NavigationRail y el contenido
    page.add(
        ft.Row(
            [
                rail,  # NavigationRail fijo a la izquierda
                ft.VerticalDivider(width=1),  # Separador vertical
                ft.Container(
                    content,
                    expand=True,
                    alignment=ft.alignment.top_left,  # Contenido pegado al margen superior izquierdo
                    padding=10,
                ),
            ],
            expand=True,
        )
    )

    # Inicializar contenido predeterminado (Usuarios)
    on_navigation_change()

ft.app(target=main)