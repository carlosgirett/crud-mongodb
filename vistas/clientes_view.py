import flet as ft

def mostrar_clientes_view(page: ft.Page, content: ft.Column, db, clientes_table):
    print("Vista de Clientes cargada")
    page.title = "Gestión de Clientes"
    page.window_width = 1335
    page.window_height = 800

    #variables de paginacion
    clientes_por_pagina = 10
    pagina_actual = 0
    cliente_seleccionado = None

    #varibles para la busqueda
    tf_buscar = ft.TextField(label="Buscar Cliente", width=200)
    clientes_filtrados = []

    #tiulo princiopal
    titulo = ft.Text("Gestión de Clientes", size=24, weight="bold")

    #campos de entrada de clientes
    tf_nombre = ft.TextField(label="Nombre")
    tf_apellido = ft.TextField(label="Apellido")
    tf_ruc = ft.TextField(label="Ruc")
    tf_direccion = ft.TextField(label="Direccion")
    tf_fecha_nacimiento = ft.TextField(label="Fecha de Nacmiento aa-mm-dd")

    #limpia los campos de texto
    def limpiar_campos():
        tf_nombre.value = ""
        tf_apellido.value = ""
        tf_ruc.value = ""
        tf_direccion.value = ""
        tf_fecha_nacimiento.value = ""
        tf_buscar.value = ""
        page.update()

    #funcion que carga los valores en la tabla
    def cargar_clientes(pagina, clientes=None, clientes_por_pagina=10):
        nonlocal clientes_filtrados
        customers = clientes if clientes is not None else db.get_all_documents("clientes")
        if not clientes:
            clientes_filtrados = customers

        clientes_table.rows.clear()
        inicio = pagina * clientes_por_pagina
        fin = inicio + clientes_por_pagina
        clientes_por_pagina = clientes_filtrados[inicio:fin]

        for customers in clientes_por_pagina:
            clientes_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(customers.get("nombre", ""))),
                        ft.DataCell(ft.Text(customers.get("apellido", ""))),
                        ft.DataCell(ft.Text(customers.get("ruc", ""))),
                        ft.DataCell(ft.Text(customers.get("direccion", ""))),
                        ft.DataCell(ft.Text(customers.get("fecha_nacimiento", ""))),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT, on_click=seleccionar_cliente, data=customers["_id"]),
                            ft.IconButton(icon=ft.icons.DELETE, on_click=eliminar_fila, data=customers["_id"])
                        ]))
                    ]
                )
            )

        #Actualiza el estao de los botones de paginacion
        btn_anterior.disabled = pagina_actual <=0
        btn_siguiente.disabled = fin >= len(clientes_filtrados)
        page.update()

    def cambiar_pagina(incremento):
        nonlocal pagina_actual
        pagina_actual += incremento
        if pagina_actual < 0:
            pagina_actual = 0
        cargar_clientes(pagina_actual, clientes_filtrados)

    def guardar_cliente(e):
        if not(
            tf_nombre.value.strip() and tf_apellido.value.strip() and  tf_ruc.value.strip() and tf_direccion.value.strip() and tf_fecha_nacimiento.value.strip()):
            dialog = ft.AlertDialog(
                title=ft.Text("Advertencia"),
                content=ft.Text("Por favor, complete todos los campos antes de continuar."),
                actions=[ft.TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            return

        nuevo_cliente = {
            "nombre":tf_nombre.value,
            "apellido": tf_apellido.value,
            "ruc": tf_ruc.value,
            "direccion": tf_direccion.value,
            "fecha_nacimiento": tf_fecha_nacimiento.value
        }

        if db:
            try:
                db.insert_document("clientes", nuevo_cliente)
            except Exception as ex:
                dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"No se pudo guardar el cliente: {ex}"),
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
        cargar_clientes(pagina_actual)

    def modificar_cliente(e):
        if not cliente_seleccionado or not(
            tf_nombre.value.strip() and tf_apellido.value.strip() and  tf_ruc.value.strip() and tf_direccion.value.strip() and tf_fecha_nacimiento.value.strip()):
            dialog = ft.AlertDialog(
                title=ft.Text("Advertencia"),
                content=ft.Text("Por favor, seleccione una fila para modificar."),
                actions=[ft.TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            return

        db.update_document("clientes", {"_id": cliente_seleccionado},{
            "$set":{
                "nombre":tf_nombre.value,
                "apellido":tf_apellido.value,
                "ruc":tf_ruc.value,
                "direccion": tf_direccion.value,
                "fecha_nacimiento":tf_fecha_nacimiento.value
            }
        })
        limpiar_campos()
        cargar_clientes(pagina_actual)

    def eliminar_fila(e):
        fila_id = e.control.data
        db.delete_document("clientes", {"_id": fila_id})
        cargar_clientes(pagina_actual)

    def seleccionar_cliente(e):
        nonlocal cliente_seleccionado
        fila_id = e.control.data
        cliente = db.get_document("clientes", {"_id": fila_id})
        if cliente:
            cliente_seleccionado = fila_id
            tf_nombre.value = cliente.get("nombre", "")
            tf_apellido.value = cliente.get("apellido", "")
            tf_ruc.value = cliente.get("ruc", "")
            tf_direccion.value = cliente.get("direccion", "")
            tf_fecha_nacimiento.value = cliente.get("fecha_nacimiento", "")
            page.update()

    def cerrar_dialogo(dialog):
        dialog.open = False
        page.update()

    def buscar_cliente(e):
        nonlocal clientes_filtrados
        query = tf_buscar.value.strip().lower()
        if query:
            clientes_filtrados = [customers for customers in db.get_all_documents("clientes") if
                                    query in customers.get("nombre", "").lower()]
        else:
            clientes_filtrados = db.get_all_documents("clientes")
        cargar_clientes(pagina_actual, clientes_filtrados)

    btn_anterior = ft.IconButton(icon=ft.icons.ARROW_LEFT, on_click=lambda e: cambiar_pagina(-1))
    btn_siguiente = ft.IconButton(icon=ft.icons.ARROW_RIGHT, on_click=lambda e: cambiar_pagina(1))
    btn_buscar = ft.OutlinedButton(text="Buscar", on_click=buscar_cliente)

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

    submit = ft.OutlinedButton(text="Guardar", on_click=guardar_cliente)
    modificar_button = ft.OutlinedButton(text="Modificar", on_click=modificar_cliente)
    limpiar_button = ft.OutlinedButton(text="Limpiar Campos", on_click=lambda e: limpiar_campos())
    botones_row = ft.Row([submit, modificar_button, limpiar_button], spacing=10)

    espacio = ft.Container(height=20)

    content.controls.clear()
    content.controls.append(
        ft.Column(
                [
                titulo,
                ft.Row([tf_nombre, tf_apellido, tf_ruc], spacing=10),
                ft.Row([tf_direccion, tf_fecha_nacimiento], spacing=10),
                botones_row,
                espacio,
                navegacion_row,
                clientes_table,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
    )

    cargar_clientes(pagina_actual)
    page.update()