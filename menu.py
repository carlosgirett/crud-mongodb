import flet as ft
from conexion.conexion import MongoDBConnection
from vistas.usuarios_view import mostrar_usuarios_view
from vistas.clientes_view import mostrar_clientes_view
from vistas.productos_view import mostrar_productos_view

def main(page: ft.Page, cerrar_sesion_callback=None):
    page.title = "Barra de Navegación"
    page.window.resizable = True
    page.window.width = 1200
    page.window.height = 800
    page.window_x = 1
    page.window_y = 1
    page.padding = 0
    page.spacing = 0

    # Conexión a MongoDB
    db = MongoDBConnection()

    # Contenedor de contenido dinámico
    content = ft.Column([], alignment=ft.MainAxisAlignment.START, expand=True, scroll="auto")

    # Definición de la usuarios table  para mostrar información de usuarios
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

    # Definición de la clientes table  para mostrar información de clientes
    clientes_table = ft.DataTable(
        border=ft.border.all(1, "grey"),
        border_radius=10,
        vertical_lines=ft.BorderSide(1, "grey"),
        width=1000,
        columns=[
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Apellido")),
            ft.DataColumn(ft.Text("RUC")),
            ft.DataColumn(ft.Text("Dirección")),
            ft.DataColumn(ft.Text("Fecha de Nacimiento")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
    )

    # Definición de la productos table  para mostrar información de productos
    productos_table = ft.DataTable(
        border=ft.border.all(1, "grey"),
        border_radius=10,
        vertical_lines=ft.BorderSide(1, "grey"),
        width=1500,
        columns=[
            ft.DataColumn(ft.Text("Nombre", size=14,width=57)),
            ft.DataColumn(ft.Text("Marca", size=14)),
            ft.DataColumn(ft.Text("Precio de \nCompra", size=14)),
            ft.DataColumn(ft.Text("Precio de \nVenta", size=14)),
            ft.DataColumn(ft.Text("Stock \nDisponible", size=14,width=57)),
            ft.DataColumn(ft.Text("Cantidad \nMínima", size=14)),
            ft.DataColumn(ft.Text("Proveedor", size=14)),
            ft.DataColumn(ft.Text("Estado", size=14)),
            ft.DataColumn(ft.Text("Acciones", size=14)),
        ],
        rows=[],
    )

    # Función y configuración para gestionar la navegación entre diferentes vistas (Usuarios, Clientes, Productos)
    # mediante un Navigation Rail, actualizando el contenido de la página según la selección del usuario.
    def on_navigation_change(e=None):
        selected_index = rail.selected_index
        content.controls.clear()
        if selected_index == 0:
            mostrar_usuarios_view(page, content, db, users_table)
        elif selected_index == 1:
            mostrar_clientes_view(page, content, db, clientes_table)
        elif selected_index == 2:
            mostrar_productos_view(page, content, db, productos_table)
        page.update()

    rail = ft.NavigationRail(
        min_width=80,
        min_extended_width=300,
        group_alignment=-0.9,
        selected_index=0,
        on_change=on_navigation_change,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icon(ft.Icons.PERSON), label="Usuarios"),
            ft.NavigationRailDestination(icon=ft.Icon(ft.Icons.SUPERVISED_USER_CIRCLE), label="Clientes"),
            ft.NavigationRailDestination(icon=ft.Icon(ft.Icons.SHOPIFY), label="Productos"),
        ],
    )

    # Botón de cierre de sesión que muestra un ícono de logout y ejecuta la función de cierre de sesión
    # al hacer clic, si está definida.
    logout_button = ft.IconButton(
        icon=ft.icons.LOGOUT_ROUNDED,
        icon_color="red",
        tooltip="Cerrar Sesión",
        on_click=lambda e: cerrar_sesion_callback(page) if cerrar_sesion_callback else None
    )

    # Agrega un destino al Navigation Rail para cerrar sesión, con el botón de logout como ícono.
    rail.destinations.append(
        ft.NavigationRailDestination(
            icon=logout_button,
            label="Salir"
        )
    )

    # Usa un Container para envolver el contenido y agregar el padding
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=0),
                ft.Container(content, expand=True, alignment=ft.alignment.top_left, padding=ft.padding.only(right=20, bottom=6))
    ],
            expand=True,
        )
    )

    on_navigation_change()

if __name__ == "__main__":
    ft.app(target=main)