from flet import *
from conexion.conexion import MongoDBConnection


def main(page: Page):
    page.title = "Gestión de Usuarios"
    db = MongoDBConnection()
    page.window_width = 1335
    page.window_height = 700

    # Variables para la paginación
    usuarios_por_pagina = 10
    pagina_actual = 0
    usuario_seleccionado = None

    # Título principal sin margen
    titulo = Text("Gestión de usuarios", size=24, weight="bold")

    # Campos de entrada de usuario
    tf_user = TextField(label="Nombre de Usuario")
    tf_password = TextField(label="Clave")
    tf_email = TextField(label="E-mail")
    tf_rol = TextField(label="Rol")
    tf_estado = TextField(label="Estado")

    # Función para guardar un nuevo usuario en la base de datos
    def guardar_usuario(e):
        if not (
                tf_user.value.strip() and tf_password.value.strip() and tf_email.value.strip() and tf_rol.value.strip() and tf_estado.value.strip()):
            print("Todos los campos son obligatorios")
            dialog = AlertDialog(
                title=Text("Advertencia"),
                content=Text("Por favor, complete todos los campos antes de continuar."),
                actions=[
                    TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))
                ]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            return
        nuevo_usuario = {
            "nombre": tf_user.value,
            "clave": tf_password.value,
            "email": tf_email.value,
            "rol": tf_rol.value,
            "estado": tf_estado.value
        }
        db.insert_document("usuarios", nuevo_usuario)
        print("Usuario guardado:", nuevo_usuario)
        limpiar_campos()
        cargar_usuarios(pagina_actual)
        page.update()

    # Función para cerrar el diálogo
    def cerrar_dialogo(dialog):
        dialog.open = False
        page.update()

    # Función para limpiar campos
    def limpiar_campos():
        tf_user.value = ""
        tf_password.value = ""
        tf_email.value = ""
        tf_rol.value = ""
        tf_estado.value = ""

    # Función para modificar usuario
    def modificar_usuario(e):
        if not usuario_seleccionado or not (
                tf_user.value.strip() and tf_password.value.strip() and tf_email.value.strip() and tf_rol.value.strip() and tf_estado.value.strip()):
            print("Seleccione una fila que desee modificar")
            dialog = AlertDialog(
                title=Text("Advertencia"),
                content=Text("Por favor, seleccione una fila para modificar."),
                actions=[
                    TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))
                ]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            return

        db.update_document("usuarios", {"_id": usuario_seleccionado}, {
            "$set": {
                "nombre": tf_user.value,
                "clave": tf_password.value,
                "email": tf_email.value,
                "rol": tf_rol.value,
                "estado": tf_estado.value
            }
        })
        print(f"Usuario Modificado: ID {usuario_seleccionado}")
        limpiar_campos()
        cargar_usuarios(pagina_actual)

    # Botones para guardar y modificar
    submit = OutlinedButton(text="Guardar", on_click=guardar_usuario)
    modificar_button = OutlinedButton(text="Modificar", on_click=modificar_usuario)

    # Crear un Row para los botones
    botones_row = Row([submit, modificar_button], spacing=10)

    # Configuración de la tabla
    users_table = DataTable(
        border=border.all(1, "grey"),
        border_radius=10,
        vertical_lines=BorderSide(1, "grey"),
        width=1000,
        columns=[
            DataColumn(Text("Nombre")),
            DataColumn(Text("Clave")),
            DataColumn(Text("E-mail")),
            DataColumn(Text("Rol")),
            DataColumn(Text("Estado")),
            DataColumn(Text("Acciones"))
        ],
        rows=[],
    )

    # Función para mostrar datos de usuarios con paginación
    def cargar_usuarios(pagina):
        users = db.get_all_documents("usuarios")
        users_table.rows.clear()
        inicio = pagina * usuarios_por_pagina
        fin = inicio + usuarios_por_pagina
        usuarios_pagina = users[inicio:fin]

        for user in usuarios_pagina:
            users_table.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(user.get("nombre", ""))),
                        DataCell(Text(user.get("clave", ""))),
                        DataCell(Text(user.get("email", ""))),
                        DataCell(Text(user.get("rol", ""))),
                        DataCell(Text(user.get("estado", ""))),
                        DataCell(Row(
                            [
                                IconButton(
                                    icon=icons.EDIT,
                                    on_click=seleccionar_usuario,
                                    data=user["_id"]
                                ),
                                IconButton(
                                    icon=icons.DELETE,
                                    on_click=eliminar_fila,
                                    data=user["_id"]
                                )
                            ]
                        ))
                    ]
                )
            )

        btn_anterior.disabled = pagina == 0
        btn_siguiente.disabled = fin >= len(users)
        page.update()

    # Función para manejar el evento de eliminar
    def eliminar_fila(e):
        fila_id = e.control.data
        db.delete_document("usuarios", {"_id": fila_id})
        print(f"Se ha eliminado el documento con ID: {fila_id}")
        cargar_usuarios(pagina_actual)

    # Función para asignar campos de texto al documento seleccionado para modificar
    def seleccionar_usuario(e):
        nonlocal usuario_seleccionado
        fila_id = e.control.data
        usuario = db.get_document("usuarios", {"_id": fila_id})
        if usuario:
            usuario_seleccionado = fila_id
            tf_user.value = usuario.get("nombre", "")
            tf_password.value = usuario.get("clave", "")
            tf_email.value = usuario.get("email", "")
            tf_rol.value = usuario.get("rol", "")
            tf_estado.value = usuario.get("estado", "")
            page.update()

    # Funciones para la navegación entre páginas
    def anterior_pagina(e):
        nonlocal pagina_actual
        if pagina_actual > 0:
            pagina_actual -= 1
            cargar_usuarios(pagina_actual)

    def siguiente_pagina(e):
        nonlocal pagina_actual
        pagina_actual += 1
        cargar_usuarios(pagina_actual)

    # Botones de navegación en el margen superior derecho
    btn_anterior = ElevatedButton("<", on_click=anterior_pagina, disabled=True)
    btn_siguiente = ElevatedButton(">", on_click=siguiente_pagina)
    paginacion_controls = Row([btn_anterior, btn_siguiente], alignment="end")

    # Cargar los usuarios de la primera página al iniciar
    cargar_usuarios(pagina_actual)

    # Columna de inputs y botones
    inputs_column = Column([titulo, tf_user, tf_password, tf_email, tf_rol, tf_estado, botones_row], spacing=10,
                           width=300)

    # Columna de la tabla y los controles de paginación, más amplia, con alineación superior
    table_column = Column([paginacion_controls, users_table], expand=True)

    # Organizar el diseño en la página
    page.add(Row([inputs_column, table_column], alignment="start", vertical_alignment="start"))


# Ejecuta la aplicación
app(target=main)