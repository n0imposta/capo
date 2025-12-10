# modules/db.py
import mysql.connector

def get_connection(config):
    try:
        conn = mysql.connector.connect(
            host=config["db_host"],
            user=config["db_user"],
            password=config["db_pass"],
            database=config["db_name"],
        )
        return conn

    except mysql.connector.Error as err:
        print("❌ Error conectando a MySQL:", err)
        return None
