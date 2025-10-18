import pymysql

def menu(cur):
    entrada = False
    while entrada == False:
        nombre = input("Ingrese el nombre del cliente: ")
        
        cur.execute("select marca from clientes where marca = %s", (nombre,))
        output = cur.fetchall()
        if len(output) > 0:
            entrada = True
        else:
            print("Ingreso invalido, intente nuevamente")
    

def puedoProducir(cursor):
    id_producto = (input("Ingrese el ID del producto a verificar: "))
    cantidad = int(input("Ingrese la cantidad a verificar: "))
    cursor.callproc("Check_Stock_Producto_2",(id_producto, cantidad))
    output = cursor.fetchall()
    for row in output:
        stock = row[1]
        if stock == "S":
            print("Se puede producir el producto solicitado.")
        else:
            print("No se puede producir el producto solicitado debido a falta de stock.")
       


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
    
    # Select query
    cur.execute("select * from clientes")
    output = cur.fetchall()
    
    for i in output:
        print(i)
    
    puedoProducir(cur)




    # Cerrar conexion
    conn.close()
    

# Codigo principal
if __name__ == "__main__" :
    mysqlconnect()



