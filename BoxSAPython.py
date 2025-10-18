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
    
    menu(cur)




    # Cerrar conexion
    conn.close()
    

# Codigo principal
if __name__ == "__main__" :
    mysqlconnect()



