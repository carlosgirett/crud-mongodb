import flet as ft
def mostrar_productos_view(page: ft.Page, content: ft.Column, db, productos_table):
    print("Vista de productos cargada")
    page.title = "Gestión de Productos"
    page.window_width = 1435
    page.window_height = 770

    # Variables de paginación
    productos_por_pagina = 10
    pagina_actual = 0
    producto_seleccionado = None

    # Variables para la búsqueda
    tf_buscar = ft.TextField(label="Buscar Producto", width=200)
    productos_filtrados = []

    # Título principal
    titulo = ft.Text("Gestión de Productos", size=24, weight="bold")

    # Campos de entrada de productos
    tf_nombre = ft.TextField(label="Nombre")
    tf_marca = ft.TextField(label="Marca")
    tf_precio_compra = ft.TextField(label="Precio de compra")
    tf_precio_venta = ft.TextField(label="Precio de venta")
    tf_stock = ft.TextField(label="Stock")
    tf_cantidad_minima = ft.TextField(label="Cantidad Minima")
    tf_proveedor = ft.TextField(label="Proveedor")
    tf_estado = ft.TextField(label="Estado")

    # Limpiar los campos de texto
    def limpiar_campos():
        tf_nombre.value = ""
        tf_marca.value = ""
        tf_precio_compra.value = ""
        tf_precio_venta.value = ""
        tf_stock.value = ""
        tf_cantidad_minima.value = ""
        tf_proveedor.value = ""
        tf_estado.value = ""
        tf_buscar.value = ""
        page.update()

    # Función que carga los valores en la tabla
    def cargar_productos(pagina, productos=None, productos_por_pagina=10):
        nonlocal productos_filtrados
        products = productos if productos is not None else db.get_all_documents("productos")
        if not productos:
            productos_filtrados = products

        productos_table.rows.clear()
        inicio = pagina * productos_por_pagina
        fin = inicio + productos_por_pagina
        productos_por_pagina = productos_filtrados[inicio:fin]


        # Agregar contenido a la tabla
        # Cambiar wrap por max_lines en cada celda
        for product in productos_por_pagina:
            productos_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(product.get("nombre", ""), max_lines=3)  # Ajustar el texto a máximo 2 líneas
                        ),
                        ft.DataCell(
                            ft.Text(product.get("marca", ""), max_lines=3)
                        ),
                        ft.DataCell(
                            ft.Text(product.get("Precio_compra", ""), max_lines=3)
                        ),
                        ft.DataCell(
                            ft.Text(product.get("precio_venta", ""), max_lines=3)
                        ),
                        ft.DataCell(
                            ft.Text(product.get("stock_disponible", ""), max_lines=3)
                        ),
                        ft.DataCell(
                            ft.Text(product.get("cantidad_minima", ""), max_lines=3)
                        ),
                        ft.DataCell(
                            ft.Text(product.get("proveedor", ""), max_lines=3)
                        ),
                        ft.DataCell(
                            ft.Text(product.get("estado", ""), max_lines=3)
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(icon=ft.icons.EDIT, on_click=seleccionar_producto, data=product["_id"]),
                                ft.IconButton(icon=ft.icons.DELETE, on_click=eliminar_fila, data=product["_id"])
                            ])
                        )
                    ]
                )
            )
        # Actualiza el estado de los botones de paginación
        btn_anterior.disabled = pagina_actual <= 0
        btn_siguiente.disabled = fin >= len(productos_filtrados)
        page.update()

    # Resto del código...

    def cambiar_pagina(incremento):
        nonlocal pagina_actual
        pagina_actual += incremento
        if pagina_actual < 0:
            pagina_actual = 0
        cargar_productos(pagina_actual, productos_filtrados)

    def guardar_producto(e):
        if not(
            tf_nombre.value.strip() and tf_marca.value.strip() and tf_precio_compra.value.strip() and tf_precio_venta.value.strip() and tf_stock.value.strip() and tf_cantidad_minima.value.strip() and tf_proveedor.value.strip() and tf_estado.value.strip()):
            dialog = ft.AlertDialog(
                title=ft.Text("Advertencia"),
                content=ft.Text("Por favor, complete todos los campos antes de continuar."),
                actions=[ft.TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            return

        nuevo_producto = {
            "nombre": tf_nombre.value,
            "marca": tf_marca.value,
            "Precio_compra": tf_precio_compra.value,
            "precio_venta": tf_precio_venta.value,
            "stock_disponible": tf_stock.value,
            "cantidad_minima": tf_cantidad_minima.value,
            "proveedor": tf_proveedor.value,
            "estado": tf_estado.value
        }

        if db:
            try:
                db.insert_document("productos", nuevo_producto)
            except Exception as ex:
                dialog = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text(f"No se pudo guardar el producto: {ex}"),
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
        cargar_productos(pagina_actual)

    def modificar_producto(e):
        if not producto_seleccionado or not(
            tf_nombre.value.strip() and tf_marca.value.strip() and tf_precio_compra.value.strip() and tf_precio_venta.value.strip() and tf_stock.value.strip() and tf_cantidad_minima.value.strip() and tf_proveedor.value.strip() and tf_estado.value.strip()):
            dialog = ft.AlertDialog(
                title=ft.Text("Advertencia"),
                content=ft.Text("Por favor, seleccione una fila para modificar."),
                actions=[ft.TextButton("Aceptar", on_click=lambda e: cerrar_dialogo(dialog))]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            return

        db.update_document("productos", {"_id": producto_seleccionado}, {
            "$set": {
                "nombre": tf_nombre.value,
                "marca": tf_marca.value,
                "Precio_compra": tf_precio_compra.value,
                "precio_venta": tf_precio_venta.value,
                "stock_disponible": tf_stock.value,
                "cantidad_minima": tf_cantidad_minima.value,
                "proveedor": tf_proveedor.value,
                "estado": tf_estado.value
            }
        })
        limpiar_campos()
        cargar_productos(pagina_actual)

    def eliminar_fila(e):
        fila_id = e.control.data
        db.delete_document("productos", {"_id": fila_id})
        cargar_productos(pagina_actual)

    def seleccionar_producto(e):
        nonlocal producto_seleccionado
        fila_id = e.control.data
        producto = db.get_document("productos", {"_id": fila_id})
        if producto:
            producto_seleccionado = fila_id
            tf_nombre.value = producto.get("nombre", "")
            tf_marca.value = producto.get("marca", "")
            tf_precio_compra.value = producto.get("Precio_compra", "")
            tf_precio_venta.value = producto.get("precio_venta", "")
            tf_stock.value = producto.get("stock_disponible", "")
            tf_cantidad_minima.value = producto.get("cantidad_minima", "")
            tf_proveedor.value = producto.get("proveedor", "")
            tf_estado.value = producto.get("estado", "")
            page.update()

    def cerrar_dialogo(dialog):
        dialog.open = False
        page.update()

    def buscar_producto(e):
        nonlocal productos_filtrados
        query = tf_buscar.value.strip().lower()
        if query:
            productos_filtrados = [product for product in db.get_all_documents("productos") if
                                   query in product.get("nombre", "").lower()]
        else:
            productos_filtrados = db.get_all_documents("productos")
        cargar_productos(pagina_actual, productos_filtrados)

    btn_anterior = ft.IconButton(icon=ft.icons.ARROW_LEFT, on_click=lambda e: cambiar_pagina(-1))
    btn_siguiente = ft.IconButton(icon=ft.icons.ARROW_RIGHT, on_click=lambda e: cambiar_pagina(1))
    btn_buscar = ft.OutlinedButton(text="Buscar", on_click=buscar_producto)

    navegacion_row = ft.Row([
            tf_buscar,
            btn_buscar,
            btn_anterior,
            btn_siguiente,
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=10
    )

    submit = ft.OutlinedButton(text="Guardar", on_click=guardar_producto)
    modificar_button = ft.OutlinedButton(text="Modificar", on_click=modificar_producto)
    limpiar_button =  ft.OutlinedButton(text="Limpiar Campos", on_click=lambda e: limpiar_campos())
    botones_row = ft.Row([submit, modificar_button, limpiar_button], spacing=10)

    espacio = ft.Container(height=20)

    content.controls.clear()
    content.controls.append(
        ft.Column(
                    [
                titulo,
                ft.Row([tf_nombre, tf_marca, tf_precio_compra], spacing=10),
                ft.Row([tf_precio_venta, tf_stock, tf_cantidad_minima], spacing=10),
                ft.Row([tf_proveedor, tf_estado], spacing=10),
                botones_row,
                espacio,
                navegacion_row,
                productos_table
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
    )
    cargar_productos(pagina_actual)
    page.update()