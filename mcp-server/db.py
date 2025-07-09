import mysql.connector
from mysql.connector import Error

# Konfiguration zentral verwalten
DB_CONFIG = {
        "user": "jdoctolero",
        "password": "veD1FM96coQasP5cj7Lt",
        "host": "mysql-server",
        "database": "jdoctolero_db"
}

def get_connection():
    """Stellt eine Verbindung zur Datenbank her und gibt das Connection-Objekt zurück."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print("❌ Fehler bei der Verbindung:", e)
        return None

