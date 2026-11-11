from db import get_connect
import bcrypt

def obtener_passw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    

def verificar_hash(password: str, hashed: str) -> bool:
    
    return bcrypt.checkpw(password.encode(), hashed)


#CREAR USUARIO
def crear_users(first_name,last_name,email,password):
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
       password = obtener_passw(password)
       sql = "INSERT INTO users (first_name,last_name,email,password,role_id) VALUES (%s,%s,%s,%s,%s)"
       cursor.execute(sql,(first_name,last_name,email,password,2))
       conn.commit()
       return {"Msj":"Creado exitosamente"}

   finally:
       cursor.close()
       conn.close()


#LOGIN
def buscar_user(email):
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
      sql = "SELECT * FROM users WHERE email = %s"
      cursor.execute(sql,(email,))
      return cursor.fetchone()
   finally:
      cursor.close()
      conn.close()
      

    

#Search for id
def buscar_id(id):
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
      sql = "SELECT first_name, role_id FROM users WHERE id = %s"
      cursor.execute(sql,(id,))
      return cursor.fetchone()
   finally:
      cursor.close()
      conn.close()

#GET PARA ASIGNADOS
def asignados():
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
      sql = """ 
      
            select equipo.model AS equipo, employees.first_name AS empleado, users.first_name AS tecnico
            from equipo
            join asignaciones on asignaciones.equipo_id = equipo.id AND asignaciones.returned_at IS NULL
            join employees on employees.id = asignaciones.employee_id
            join users on users.id = asignaciones.assigned_by  
            
            """
      cursor.execute(sql)
      return cursor.fetchall()
   finally:
      cursor.close()
      conn.close()


#GET PARA EQUIPOS DISPONIBLES
def disponibles():
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
      sql = """

         select  equipo.id, equipo.model, equipos_status.name 
         from equipo
         join equipos_status on equipo.status_id = equipos_status.id
         where equipos_status.id = 1

         """
      cursor.execute(sql)
      return cursor.fetchall()
   finally:
      cursor.close()
      conn.close()


#GET PARA EQUIPOS reparaciones
def reparaciones():
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
      sql = """

         select equipo.id, equipo.model, equipos_status.name 
         from equipo
         join equipos_status on equipo.status_id = equipos_status.id
         where equipos_status.id = 3

         """
      cursor.execute(sql)
      return cursor.fetchall()
   finally:
      cursor.close()
      conn.close()


#GET PARA EQUIPOS DAMAGED
def damaged():
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
      sql = """

         select  equipo.id, equipo.model, equipos_status.name 
         from equipo
         join equipos_status on equipo.status_id = equipos_status.id
         where equipos_status.id = 4

         """
      cursor.execute(sql)
      return cursor.fetchall()
   finally:
      cursor.close()
      conn.close()



#GET PARA EQUIPOS RETIRADOS
def retirados():
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
      sql = """

         select  equipo.model, equipos_status.name 
         from equipo
         join equipos_status on equipo.status_id = equipos_status.id
         where equipos_status.id = 5

         """
      cursor.execute(sql)
      return cursor.fetchall()
   finally:
      cursor.close()
      conn.close()



#POST AGREGAR EQUIPOS
def insertar(equipo_type_id, brand, model, serial_number, purchase_date, warranty_end, description):
   conn = get_connect()
   cursor = conn.cursor()

   try:
      sql = "INSERT INTO equipo (equipo_type_id, status_id, brand, model, serial_number, purchase_date, warranty_end, description) VALUES (%s,1,%s,%s,%s,%s,%s,%s)"
      cursor.execute(sql, (equipo_type_id, brand, model, serial_number, purchase_date, warranty_end, description))
      conn.commit()
   finally:
      cursor.close()
      conn.close()



#POST ASIGNAR EQUIPOS
def asignar(equipo_id, employee_id, assigned_by,notes):
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
      cursor.execute("SELECT status_id from equipo WHERE id = %s ", (equipo_id,))
      equipo = cursor.fetchone()

      if equipo is None:
         raise ValueError("Equipo no existe")

      if equipo['status_id'] == 2:
         raise ValueError("El equipo ya esta asignado")
      
      if equipo['status_id'] == 3:
         raise ValueError("El equipo esta en reparacion")
      
      if equipo['status_id'] == 4:
         raise ValueError("El equipo esta en damaged")

      

      sql = "INSERT INTO asignaciones (equipo_id, employee_id, assigned_by,notes) VALUES (%s, %s, %s, %s)"
      cursor.execute(sql, (equipo_id, employee_id, assigned_by,notes))
      
      sql = "UPDATE equipo SET status_id = 2 WHERE id = %s"
      cursor.execute(sql, (equipo_id,))
      
      conn.commit()

      return {
            "equipo_id": equipo_id,
            "employee_id": employee_id,
            "assigned_by": assigned_by,
            "notes": notes
        }

   except Exception:
      conn.rollback()
      raise
      
   finally:
      cursor.close()
      conn.close()

#POST PARA MANDAR A DAMAGED
def m_damaged(id):
    conn = get_connect()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT status_id FROM equipo WHERE id = %s",
            (id,)
        )

        equipo = cursor.fetchone()

        if equipo is None:
            raise ValueError("Equipo no existe")

        if equipo["status_id"] == 4:
            raise ValueError("El equipo ya esta en damaged")

        cursor.execute(
            "UPDATE equipo SET status_id = 4 WHERE id = %s",
            (id,)
        )

        cursor.execute("UPDATE asignaciones SET returned_at = NOW() WHERE equipo_id = %s AND returned_at IS NULL",(id,))

        conn.commit()

        respuesta = {
            "id_del_equipo": id,
            "msj": "Se envio a damaged"
        }

        return respuesta

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        raise

    finally:
        cursor.close()
        conn.close()

#POST PARA MANDAR A REPARACION
def m_reparacion(id, reported_by, description):
    conn = get_connect()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT status_id FROM equipo WHERE id = %s",
            (id,)
        )

        equipo = cursor.fetchone()

        if equipo is None:
            raise ValueError("Equipo no existe")

        if equipo["status_id"] == 3:
            raise ValueError("El equipo ya esta en reparacion")

        cursor.execute(
            "UPDATE equipo SET status_id = 3 WHERE id = %s AND status_id = 4 ",
            (id,)
        )

        if cursor.rowcount == 0:
            raise ValueError("El equipo ya no está disponible para reparación")


        cursor.execute("INSERT INTO mantenimiento (equipo_id, reported_by, description,start_date,status_id,created_at) VALUES (%s, %s, %s, NOW(),1,NOW())",
                       (id, reported_by,description))

        conn.commit()

        respuesta = {
            "id_del_equipo": id,
            "msj": "Se envio a reparacion, mira su progeso en mantenimiento"
        }

        return respuesta

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        raise

    finally:
        cursor.close()
        conn.close()

#POST SALIDA DE EQUIPO DE MANTENIMIENTO
def salida_mant(id):
    conn = get_connect()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT equipo_id,status_id FROM mantenimiento WHERE id = %s",
            (id,)
        )

        mantenimiento = cursor.fetchone()

        if mantenimiento is None:
            raise ValueError("No existe el mantenimiento")
        if mantenimiento["status_id"] == 2:
           raise ValueError("El equipo ya salio de mantenimiento")

        equipo_id = mantenimiento["equipo_id"]
        cursor.execute(
            "UPDATE mantenimiento SET end_date = NOW(), status_id = 2 WHERE id = %s",
            (id,)
        )
        
        cursor.execute(
            "UPDATE equipo SET status_id = 1 WHERE id= %s",
            (equipo_id,)
         )

        conn.commit()

        respuesta = {
            "id_del_equipo": id,
            "msj": "Se completo el mantenimiento, el equipo ahora esta disponible"
        }

        return respuesta

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        raise

    finally:
        cursor.close()
        conn.close()

#Ver mantenimiento para reparadores
def mant():
   conn = get_connect()
   cursor = conn.cursor(dictionary=True)

   try:
    sql = "SELECT * FROM mantenimiento"

    cursor.execute(sql)

    return cursor.fetchall()

   finally:
        cursor.close()
        conn.close()

   




#-----------------------


def stats():
    conn = get_connect()
    cursor = conn.cursor(dictionary=True)

    try:
        sql = """
            SELECT
                equipos_status.id AS status_id,
                equipos_status.name AS estado,
                COUNT(equipo.id) AS total
            FROM equipos_status
            LEFT JOIN equipo
                ON equipo.status_id = equipos_status.id
            GROUP BY equipos_status.id, equipos_status.name
        """
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()