from flask_mysqldb import MySQL
from config import config
from flask import jsonify


mysql = MySQL()
development_config = config['development']

import datetime

def añadir_facturacion(usuario, cliente, fecha_venta, hora_venta, productos, total, fecha_pago, hora_pago, nota):
    try:
        conn = mysql.connection
        cursor = conn.cursor()

        # Iniciar transacción
        cursor.execute("START TRANSACTION;")

        # Paso 1: Insertar los datos en la tabla `ventas`
        sql_venta = """
            INSERT INTO ventas (id_usuario, id_cliente, fecha_venta, hora_venta)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(sql_venta, (usuario, cliente, fecha_venta, hora_venta))
        id_venta = cursor.lastrowid  # Obtener el ID de la venta recién creada

        # Paso 2: Insertar en `detalles_ventas` y verificar stock
        sql_detalles = """
            INSERT INTO detalles_ventas (id_venta, id_producto, cantidad, precio_unitario, descripcion)
            VALUES (%s, %s, %s, %s, %s);
        """
        
        for producto in productos:
            # Verificar si hay suficiente stock
            cursor.execute("SELECT nombre, stock FROM productos WHERE identificador_p = %s", (producto['id_producto'],))
            producto_data = cursor.fetchone()

            if not producto_data:
                return {"status": "error", "message": f"Producto con ID {producto['id_producto']} no encontrado."}
            
            nombre_producto, stock_disponible = producto_data

            if producto['cantidad'] > stock_disponible:
                return {"status": "error", "message": f"Stock insuficiente para el producto {nombre_producto} (ID: {producto['id_producto']}). Stock disponible: {stock_disponible}."}

            # Insertar en `detalles_ventas`
            cursor.execute(sql_detalles, (
                id_venta,
                producto['id_producto'],
                producto['cantidad'],
                producto['precio_unitario'],
                producto.get('descripcion', '')  # Valor por defecto si no hay descripción
            ))

            # Actualizar el stock del producto
            nuevo_stock = stock_disponible - producto['cantidad']
            cursor.execute("UPDATE productos SET stock = %s WHERE identificador_p = %s", (nuevo_stock, producto['id_producto']))

        # Paso 3: Insertar los datos en la tabla `pagos`
        sql_pago = """
            INSERT INTO pagos (id_venta, monto, fecha_pago, id_cliente, hora_pago, nota)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(sql_pago, (id_venta, total, fecha_pago, cliente, hora_pago, nota))

        # Paso 4: Generar la factura
        fecha_actual = datetime.date.today().strftime("%Y%m%d")
        cursor.execute("SELECT COUNT(*) FROM facturas WHERE DATE(fecha_emision) = CURDATE();")
        total_facturas_hoy = cursor.fetchone()[0]
        numero_factura = f"FAC-{fecha_actual}-{total_facturas_hoy + 1:03d}"

        sql_factura = """
            INSERT INTO facturas (numero_factura, id_venta, fecha_emision)
            VALUES (%s, %s, CURDATE());
        """
        cursor.execute(sql_factura, (numero_factura, id_venta))
        id_factura = cursor.lastrowid

        # Paso 5: Actualizar el registro en la tabla `pagos` con el `id_factura`
        sql_actualizar_pago = """
            UPDATE pagos
            SET id_factura = %s
            WHERE id_venta = %s;
        """
        cursor.execute(sql_actualizar_pago, (id_factura, id_venta))

        # Confirmar la transacción
        conn.commit()

        return {
            "status": "success",
            "message": "Factura procesada correctamente",
            "id_factura": id_factura,
            "numero_factura": numero_factura
        }
    except Exception as e:
        conn.rollback()  # Revertir la transacción en caso de error
        print(f"Error al procesar la facturación. Venta: {usuario}, Cliente: {cliente}, Total: {total}")
        print("Error:", str(e))
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
   
        
def obtener_datos_factura(cursor, id_factura):
    try:
        # Consulta los datos de la factura
        sql_factura = """
            SELECT 
                p.id_factura AS numero_factura,
                f.fecha_emision, 
                v.id_cliente, 
                c.nombres AS cliente, 
                SUM(dv.cantidad * dv.precio_unitario) AS total
            FROM pagos p
            JOIN facturas f ON p.id_factura = f.id_factura
            JOIN ventas v ON p.id_venta = v.id_venta
            JOIN clientes c ON p.id_cliente = c.identificador_c
            JOIN detalles_ventas dv ON v.id_venta = dv.id_venta
            WHERE p.id_factura = %s
            GROUP BY p.id_factura, f.fecha_emision, v.id_cliente, c.nombres;
        """
        cursor.execute(sql_factura, (id_factura,))
        factura = cursor.fetchone()

        if not factura:
            return None, "Factura no encontrada."
        
        return {
            "numero_factura": factura['numero_factura'],
            "fecha_emision": factura['fecha_emision'],
            "cliente": factura['cliente'],
            "total": factura['total']
        }, None

    except Exception as e:
        return None, str(e)
