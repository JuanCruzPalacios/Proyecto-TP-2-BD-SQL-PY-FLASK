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



