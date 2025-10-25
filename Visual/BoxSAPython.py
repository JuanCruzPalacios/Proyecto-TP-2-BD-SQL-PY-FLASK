import pymysql
import os

from flask import Flask

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template, request, jsonify
from flask import render_template, redirect, url_for, flash
from decimal import Decimal as decimal

app = Flask(__name__)

def mysqlconnect():
    # Para conectar con la base de datos
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password = "admin",
            db='boxsa',
            )
    except pymysql.MySQLError as e:
        print("Error de conexion", e)
        return
    
    cur = conn.cursor()
    return cur , conn

def ReservarStockProducto(cur, idProducto, cantidad):
    cur.callproc("reservar_stock",(idProducto, cantidad))
    output = cur.fetchall()
    if output[0][1] == "S":
        return True
    else:
        return False

def generarOrdenVenta(cur , cliente , listaProductosSeleccionados):
    # Funcion para generar la orden de venta en la base de datos
    nItem = 0
    try:
        total = 0
        for producto in listaProductosSeleccionados:
            cur.execute("SELECT MAX(id_OV) FROM ordenventa")
            idOV = cur.fetchall()[0][0] + 1
            cur.execute("SELECT MAX(id_OVDet) FROM detalleordenventa")
            idOVDet = cur.fetchall()[0][0] + 1
            cur.execute("SELECT * FROM productos WHERE idProducto = %s", (producto[0],))
            productoInfo = cur.fetchall()
            nItem += 1
            importe = (productoInfo[0][6]*int(producto[1]))
            total += importe
            cur.execute("INSERT INTO detalleordenventa (id_OVDet, id_OV, OfItem,  id_Producto, ProdDetalle , Qty , Punit , Importe) VALUES (%s, %s, %s, %s , %s , %s , %s , %s)", (idOVDet, idOV, nItem, producto[0] , productoInfo[0][2] , producto[1] , productoInfo[0][6] , importe ,))

        descuento = 0
        subtotalPrecio = float(total) * ((100 - descuento) / 100)
        cur.execute("INSERT INTO ordenventa (id_OV, id_Cliente , fecha_orden , fecha_entrega , estado , descuento , idTipoEntrega , id_empleadoVendedor , idMetodoDePago, subtotal , Total , observaciones) VALUES (%s, %s, CURDATE() , DATE_ADD(CURDATE(), INTERVAL 7 DAY) , 'P' , %s , 1 , 1 , 1 , %s , %s , 'Sin observaciones')", (idOV, cliente ,descuento , decimal(round(subtotalPrecio,2)) , total ,))
        return ("Orden de venta generada correctamente.")
    except pymysql.MySQLError as e:
        return("Error al generar la orden de venta, intente nuevamente mas tarde o contacte a soporte.", e)

    return False

# Codigo para JavaScript
@app.route('/', methods=['GET', 'POST'])
def login():
    cur , conexion = mysqlconnect()
    mensaje = ""
    if request.method == 'POST':
        cliente = request.form['marca']
        if ValidarCliente(cur, cliente)[0]:
            return redirect(url_for('index', marca = cliente , cliente=ValidarCliente(cur, cliente)[1]))
        else:
            mensaje = "Cliente no valido. Intente nuevamente."
    return render_template('login.html', mensaje=mensaje)

@app.route("/index" , methods=['GET' , 'POST'])
def index():
    global listaProductosSeleccionados
    global subtotalProductos
    cur , conexion = mysqlconnect()
    mensaje = ""
    cliente = request.args.get('cliente')
    marca = request.args.get('marca')
    listaProductos = MostrarProductosCliente(cur , cliente , listaProductosSeleccionados)
    listaOrdenesVenta = MostrarOrdenesVenta(cur , cliente)

    if request.method == 'POST':
        form_id = request.form['form_id']
        if form_id == 'form_seleccionar_producto':
            productoSeleccionado = request.form['idProducto']
            cantidad = request.form['cantidad']
            try:
                if ValidarProducto(cur , cliente , productoSeleccionado):
                    if StockDisponibleProducto(cur , productoSeleccionado , cantidad):
                        if productoSeleccionado not in [p[0] for p in listaProductosSeleccionados]:
                            listaProductosSeleccionados.append([productoSeleccionado , cantidad])
                            cur.execute("SELECT PUnitario from productos where idProducto = %s", (productoSeleccionado,))
                            pUnitario = cur.fetchall()[0][0]
                            importe = int(cantidad) * float(pUnitario)
                            subtotalProductos = subtotalProductos + importe

                        else:
                            #Sumar cantidad al producto ya seleccionado
                            for p in listaProductosSeleccionados:
                                if p[0] == productoSeleccionado:
                                    if (int(p[1]) + int(cantidad)) <= 0:
                                        mensaje = "Cantidad no valida. Intente nuevamente."
                                    else:
                                        p[1] = int(p[1]) + int(cantidad)
                                        cur.execute("SELECT PUnitario from productos where idProducto = %s", (productoSeleccionado,))
                                        pUnitario = cur.fetchall()[0][0]
                                        importe = abs(int(cantidad)) * float(pUnitario)
                                        if int(cantidad) > 0:
                                            subtotalProductos = subtotalProductos + importe
                                        else:
                                            subtotalProductos = subtotalProductos - importe

                    else:
                        mensaje = "No hay stock suficiente para producir el producto solicitado en tal cantidad."
                else:
                    mensaje = "Producto no valido. Intente nuevamente."
            except Exception as e:
                mensaje = "Error al seleccionar el producto. Revise el id y cantidad ingresada e intente nuevamente." , e
        elif form_id == 'generar_ov':
            if len(listaProductosSeleccionados) == 0:
                mensaje = "No se han seleccionado productos para generar la orden de venta."
            else:
                for producto in listaProductosSeleccionados:
                    if not ReservarStockProducto(cur , producto[0] , producto[1]):
                        mensaje = "No se pudo reservar el stock para el producto con ID: " + str(producto[0]) + ". Revise el stock disponible e intente nuevamente."
                        return render_template('index.html' , cliente=cliente , marca=marca , productos=MostrarProductosCliente(cur , cliente , listaProductosSeleccionados), productosSeleccionados = listaProductosSeleccionados, mensaje = mensaje , subtotalProductos = round(subtotalProductos,2), ordenesVenta = listaOrdenesVenta)
                mensaje = generarOrdenVenta(cur , cliente , listaProductosSeleccionados)
                listaProductosSeleccionados.clear() 
                conexion.commit()
                listaOrdenesVenta = MostrarOrdenesVenta(cur , cliente)

    return render_template('index.html' , cliente=cliente , marca=marca , productos=MostrarProductosCliente(cur , cliente , listaProductosSeleccionados), productosSeleccionados = listaProductosSeleccionados, mensaje = mensaje , subtotalProductos = round(subtotalProductos,2) , ordenesVenta = listaOrdenesVenta)

def ValidarProducto(cur , idCliente, idProducto):
    cur.execute("SELECT * from productos where idCliente = %s and idProducto = %s", (idCliente, idProducto))
    output = cur.fetchall()
    if len(output) > 0:
        return True
    else:
        return False

def ValidarCliente(cur , cliente):
        cur.execute("select idCliente from clientes where marca = %s", (cliente,))
        output = cur.fetchall()
        if len(output) > 0:
            return True , output[0][0]
        else:
            return False , None

def MostrarProductosCliente(cur , idCliente, listaProductosSeleccionados):
    cur.execute("SELECT idProducto, ProdDetalle , PUnitario from productos where idCliente = %s", (idCliente,))
    output = cur.fetchall()
    listaProductos = []
    for i in output:
        if i[0] not in [p[0] for p in listaProductosSeleccionados]:
            listaProductos.append([i[0] , i[1] , i[2]])
    return listaProductos

def StockDisponibleProducto(cur , idProducto , cantidad ):
    cur.callproc("Check_Stock_Producto_2",(idProducto, cantidad , "ok"))
    output = cur.fetchall()
    for row in output:
        stock = row[1]
        if stock == "S":
            return True
        else:
            return False

def MostrarOrdenesVenta(cur , idCliente):
    cur.execute("SELECT * from ordenventa where id_Cliente = %s", (idCliente,))
    output = cur.fetchall()
    return output

# Codigo principal
if __name__ == '__main__':
    global listaProductosSeleccionados
    listaProductosSeleccionados = []
    global subtotalProductos
    subtotalProductos = 0
    app.run(debug=True)
