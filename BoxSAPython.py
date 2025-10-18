import pymysql
import os

def LimpiarConsola():
    os.system('cls')

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
    
    cliente = IngresarCliente(cur)
    LimpiarConsola()
    print("Cliente seleccionado:", cliente)
    print("Ingrese los productos que desea producir: ")
    print(ElegirProducto(cur, cliente))


    # Cerrar conexion
    conn.close()

def ValidarProducto(cur , idCliente, idProducto):
    cur.execute("SELECT * from productos where idCliente = %s and idProducto = %s", (idCliente, idProducto))
    output = cur.fetchall()
    if len(output) > 0:
        return True
    else:
        return False

def ElegirProducto(cur , idCliente):
    listaProductos = []
    idProducto = ""
    while idProducto != "Cancelar":
        cur.execute("SELECT idProducto, ProdDetalle from productos where idCliente = %s", (idCliente,))
        output = cur.fetchall()
        print("Productos disponibles:")
        print("")
        for i in output:
            if i[0] not in [p[0] for p in listaProductos]:
                print("ID Producto:", i[0], " | Detalle:", i[1])

        print ("")
        idProducto = input("Seleccione un producto ingresando su ID o ingrese Cancelar: ")

        while ValidarProducto(cur, idCliente, idProducto) == False and idProducto not in listaProductos and idProducto != "Cancelar":
            print("El ID de producto ingresado no es valido o ya fue elegido. Intente nuevamente.")
            idProducto = input("Seleccione un producto ingresando su ID o ingrese Cancelar: ")

        if idProducto != "Cancelar":
            print("Producto seleccionado correctamente.")
            print("Informacion del producto detallada: ")
            cur.execute("SELECT * from productos where idProducto = %s", (idProducto,))
            output = cur.fetchall()
            # Formatear la informacion de producto para que sea visible para el usuario
            print("ID: " , output[0][0] , ", Detalle: " , output[0][2] , ", Costo: " , output[0][4] , ", Margen: " , output[0][5] , ", Precio unitario: " , output[0][6] , ", Estado: " , output[0][7] , ", Fecha de alta: " , output[0][8])
            Cantidad = input("Ingrese la cantidad que desea producir de este producto: ")
            listaProductos.append([idProducto , Cantidad])
            print("Productos seleccionados: ", listaProductos)
            input("Presione Enter para continuar...")
    return listaProductos

def IngresarCliente(cur):
    entrada = False
    while entrada == False:
        nombre = input("Ingrese el nombre del cliente: ")
        
        cur.execute("select idCliente from clientes where marca = %s", (nombre,))
        output = cur.fetchall()
        if len(output) > 0:
            entrada = True
            return output[0][0]
        else:
            print("Ingreso invalido, intente nuevamente")


def puedoProducir(cur):
    validado = False
    while validado == False:
        idArt = input("Ingrese el ID del articulo: ")
        cant = input("Ingrese la cantidad del articulo: ")
        cur.execute("select idArt from articulos where idArt = %s", (idArt,))
        output = cur.fetchall()

        if len(output) > 0:
            cur.execute("select cantidad from stockarticulos where id_articulo = %s", (idArt,))
            output = cur.fetchall()
            print(output)
            validado = True
        else:
            print("Ingreso invalido, intente nuevamente")
    if output >= cant:
        print("Se puede producir, sobrando ", (output - cant))
    else:
        print("No se puede producir")
    


# Codigo principal
if __name__ == "__main__" :
    mysqlconnect()