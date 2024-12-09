# Importar las bibliotecas necesarias
import flet as ft
from conexion.conexion import MongoDBConnection
from menu import main as menu_main
import logging

# Configurar logging para depuración
logging.basicConfig(level=logging.INFO)

# Variables globales para gestionar el estado de autenticación
usuario_autenticado = False
usuario_logueado = None


def main(page: ft.Page):
    """
    Función principal que configura la ventana de la aplicación
    y gestiona el flujo de inicio de sesión.
    """
    global usuario_autenticado, usuario_logueado

    # Configuración inicial de la ventana de la aplicación
    page.padding = 0
    page.spacing = 0
    page.title = "Sistema de Gestión"
    page.window.width = 1300
    page.window.height = 800
    page.window.resizable = False
    page.window_x = 0
    page.window_y = 0
    page.bgcolor = ft.colors.WHITE

    # Conexión con la base de datos
    db = MongoDBConnection()

    def cerrar_sesion(page: ft.Page):
        """
        Restablece el estado de autenticación y muestra la pantalla de login.
        """
        global usuario_autenticado, usuario_logueado
        usuario_autenticado = False
        usuario_logueado = None
        page.controls.clear()
        page.update()
        mostrar_login()

    def mostrar_login():
        """
        Muestra la interfaz de inicio de sesión.
        """

        def validar_credenciales(e):
            """
            Valida las credenciales ingresadas contra la base de datos.
            """
            global usuario_autenticado, usuario_logueado

            try:
                # Obtener valores ingresados
                usuario = username_input.value.strip()
                clave = password_input.value.strip()

                if not usuario or not clave:
                    mostrar_advertencia("Por favor, completa todos los campos.")
                    return

                # Buscar usuario en la base de datos (sin distinguir mayúsculas/minúsculas)
                user_data = db.get_document(
                    "usuarios",
                    {"nombre": {"$regex": f"^{usuario}$", "$options": "i"}}
                )

                if user_data:
                    # Verificar contraseña
                    stored_password = user_data.get("clave")
                    if clave == stored_password:
                        # Verificar si la cuenta está activa
                        if str(user_data.get("estado", "")).lower() == "true":
                            usuario_autenticado = True
                            usuario_logueado = user_data
                            mostrar_menu()
                        else:
                            mostrar_advertencia("Cuenta desactivada. Contacte al administrador.")
                    else:
                        mostrar_advertencia("Contraseña incorrecta.")
                else:
                    mostrar_advertencia("Usuario no encontrado.")
            except Exception as ex:
                # Manejo de errores de validación
                logging.error(f"Error al validar credenciales: {str(ex)}")
                mostrar_advertencia(f"Error de sistema: {str(ex)}")

        def mostrar_advertencia(mensaje):
            """
            Muestra un cuadro de diálogo con un mensaje de advertencia.
            """
            def cerrar_dialogo(e):
                page.dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(mensaje),
                actions=[ft.TextButton("Cerrar", on_click=cerrar_dialogo)]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        def mostrar_menu():
            """
            Muestra el menú principal si la autenticación es exitosa.
            """
            global usuario_autenticado
            page.controls.clear()
            page.update()

            if usuario_autenticado:
                menu_main(page, cerrar_sesion)
                page.update()

        # Componentes de la interfaz de login
        username_input = ft.TextField(
            label="Nombre de usuario",
            width=300,
            border_color=ft.colors.PRIMARY,
            focused_border_color=ft.colors.PRIMARY_CONTAINER
        )

        password_input = ft.TextField(
            label="Contraseña",
            width=300,
            password=True,
            can_reveal_password=True,
            border_color=ft.colors.PRIMARY,
            focused_border_color=ft.colors.PRIMARY_CONTAINER
        )

        login_button = ft.ElevatedButton(
            "Iniciar sesión",
            width=300,
            on_click=validar_credenciales,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.MaterialState.DEFAULT: ft.Colors.PRIMARY,
                    ft.MaterialState.HOVERED: ft.Colors.PRIMARY_CONTAINER
                },
                color={
                    ft.MaterialState.DEFAULT: ft.colors.WHITE
                }
            )
        )

        # Diseño de la pantalla de login
        login_content = ft.Row(
            [
                # Panel izquierdo con imagen
                ft.Container(
                    width=450,
                    height=800,
                    bgcolor=ft.colors.BLUE_100,
                    content=ft.Image(
                        src="/api/placeholder/500/600",
                        width=500,
                        height=600,
                        fit=ft.ImageFit.COVER
                    )
                ),
                # Panel derecho con formulario de login
                ft.Container(
                    width=500,
                    height=600,
                    padding=50,
                    content=ft.Column(
                        [
                            ft.Text(
                                "Iniciar Sesión",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.PRIMARY
                            ),
                            ft.Text(
                                "Ingrese sus credenciales",
                                size=14,
                                color=ft.colors.GREY
                            ),
                            ft.Container(height=20),
                            username_input,
                            password_input,
                            ft.Container(height=20),
                            login_button
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    )
                )
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START
        )

        # Mostrar la pantalla de login
        page.controls.clear()
        page.add(login_content)
        page.update()

    # Mostrar la pantalla de login al iniciar
    mostrar_login()


# Iniciar la aplicación
ft.app(target=main)