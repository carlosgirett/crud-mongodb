import flet as ft


def mostrar_usuarios_view(page: ft.Page, content: ft.Column, db, users_table):
    # Contenedor para mostrar contenido dinámico
    print("Vista de usuarios cargada")
    page.title = "Gestión de Usuarios"
    page.window.resizable = False

    # Variables para la paginación
    usuarios_por_pagina = 8
    pagina_actual = 0
    usuario_seleccionado = None

    # Variables de búsqueda
    tf_buscar = ft.TextField(label="Buscar usuario", width=200)
    usuarios_filtrados = []

    # Título principal
    titulo = ft.Text("Gestión de usuarios", size=24, weight="bold")

    # Campos de entrada de usuario
    tf_user = ft.TextField(label="Nombre de Usuario")
    tf_password = ft.TextField(label="Clave")
    tf_email = ft.TextField(label="E-mail")
    tf_rol = ft.TextField(label="Rol")
    tf_estado = ft.TextField(label="Estado")

    #funcion para limpiar campos
    def limpiar_campos():
        tf_user.value = ""
        tf_password.value = ""
        tf_email.value = ""
        tf_rol.value = ""
        tf_estado.value = ""
        tf_buscar.value = ""
        page.update()

    # Función para cargar los usuarios en la tabla según la página actual,
    # gestionando la paginación y actualizando la lista de productos filtrados.
    def cargar_usuarios(pagina, usuarios=None):
        nonlocal usuarios_filtrados
        users = usuarios if usuarios is not None else db.get_all_documents("usuarios")
        if not usuarios:  # Si no se especifican usuarios filtrados, utilizar los completos
            usuarios_filtrados = users

        users_table.rows.clear()
        inicio = pagina * usuarios_por_pagina
        fin = inicio + usuarios_por_pagina
        usuarios_pagina = usuarios_filtrados[inicio:fin]

        for user in usuarios_pagina:
            users_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(user.get("nombre", ""))),
                        ft.DataCell(ft.Text(user.get("clave", ""))),
                        ft.DataCell(ft.Text(user.get("email", ""))),
                        ft.DataCell(ft.Text(user.get("rol", ""))),
                        ft.DataCell(ft.Text(user.get("estado", ""))),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, on_click=seleccionar_usuario, data=user["_id"]),
                            ft.IconButton(icon=ft.icons.DELETE, on_click=eliminar_fila, data=user["_id"])
                        ]))
                    ]
                )
            )

        # Actualizar el estado de los botones de paginación
        btn_anterior.disabled = pagina_actual <= 0
        btn_siguiente.disabled = fin >= len(usuarios_filtrados)
        page.update()

    def cambiar_pagina(incremento):
        nonlocal pagina_actual
        pagina_actual += incremento
        if pagina_actual < 0:
            pagina_actual = 0
        cargar_usuarios(pagina_actual, usuarios_filtrados)

    # Función para validar los datos ingresados, guardar un nuevo usuario en la base de datos
    # y manejar posibles errores o advertencias al usuario.
    def guardar_usuario(e):
        if not (
            tf_user.value.strip() and tf_password.value.strip() and tf_email.value.strip() and tf_rol.value.strip() and tf_estado.value.strip()):
            dialog = ft.AlertDialog(
                title=ft.Text("Advertencia"),
                content=ft.Text("Por favor, complete todos los campos antes de continuar."),
                actions=[ft.TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))]
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

        if db:
            try:
                db.insert_document("usuarios", nuevo_usuario)
            except Exception as ex:
                dialog = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text(f"No se pudo guardar el usuario: {ex}"),
                    actions=[ft.TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))]
                )
                page.dialog = dialog
                dialog.open = True
                page.update()
                return
        else:
            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text("No se pudo conectar con la base de datos."),
                actions=[ft.TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            return

        limpiar_campos()
        cargar_usuarios(pagina_actual)

    # Función para modificar un usuario existente en la base de datos
    # después de validar que un usuario ha sido seleccionado y los campos están completos.
    def modificar_usuario(e):
        if not usuario_seleccionado or not (
                tf_user.value.strip() and tf_password.value.strip() and tf_email.value.strip() and tf_rol.value.strip() and tf_estado.value.strip()):
            dialog = ft.AlertDialog(
                title=ft.Text("Advertencia"),
                content=ft.Text("Por favor, seleccione una fila para modificar."),
                actions=[ft.TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))]
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
        limpiar_campos()
        cargar_usuarios(pagina_actual)

    #funcion que elimina un usuario seleccionado en la base de datos
    def eliminar_fila(e):
        fila_id = e.control.data
        db.delete_document("usuarios", {"_id": fila_id})
        cargar_usuarios(pagina_actual)

    # Función para seleccionar un usuario de la base de datos y cargar sus datos en el formulario.
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

    def cerrar_dialogo(dialog):
        dialog.open = False
        page.update()

    # Función para buscar usuarios en la base de datos según el texto ingresado
    # y actualizar la lista de productos mostrados en la interfaz.
    def buscar_usuario(e):
        nonlocal usuarios_filtrados
        query = tf_buscar.value.strip().lower()
        if query:
            usuarios_filtrados = [user for user in db.get_all_documents("usuarios") if query in user.get("nombre", "").lower()]
        else:
            usuarios_filtrados = db.get_all_documents("usuarios")
        cargar_usuarios(pagina_actual, usuarios_filtrados)

    btn_anterior = ft.IconButton(icon=ft.icons.ARROW_LEFT, on_click=lambda e: cambiar_pagina(-1))
    btn_siguiente = ft.IconButton(icon=ft.icons.ARROW_RIGHT, on_click=lambda e: cambiar_pagina(1))
    btn_buscar = ft.OutlinedButton(text="Buscar", on_click=buscar_usuario)

    navegacion_row = ft.Row(
        [
            tf_buscar,
            btn_buscar,
            btn_anterior,
            btn_siguiente,
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=10,
    )

    submit = ft.OutlinedButton(text="Guardar", on_click=guardar_usuario)
    modificar_button = ft.OutlinedButton(text="Modificar", on_click=modificar_usuario)
    limpiar_button = ft.OutlinedButton(text="Limpiar Campos", on_click=lambda e: limpiar_campos())
    botones_row = ft.Row([submit, modificar_button, limpiar_button], spacing=10)

    espacio = ft.Container(height=20)

    content.controls.clear()
    content.controls.append(
        ft.Column(
            [
                titulo,
                ft.Row([tf_user, tf_password, tf_email], spacing=10),
                ft.Row([tf_rol, tf_estado], spacing=10),
                botones_row,
                espacio,
                navegacion_row,
                users_table,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
    )

    cargar_usuarios(pagina_actual)
    page.update()