import pymysql

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
    
    # Cerrar conexion
    conn.close()

# Codigo principal
if __name__ == "__main__" :
    mysqlconnect()