from db import get_connection

def test_db_connection():
    conn = get_connection()
    if not conn:
        print("❌ Verbindung fehlgeschlagen!")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM module")
        rows = cursor.fetchall()

        if rows:
            print(f"✅ Verbindung erfolgreich!")
            for row in rows:
                print(row)
        else:
            print("keine Einträge gefunden.")
    except Exception as e:
        print(f"⚠️ Verbindung ok, aber Fehler bei SQL-Abfrage: {e}")
    finally:
        cursor.close()
        conn.close()
                 
if __name__ == "__main__":                                                      
    test_db_connection()
