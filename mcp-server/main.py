from mcp.server.fastmcp import FastMCP
from db import get_connection

mcp = FastMCP("modulhandbuch")

@mcp.tool()
def get_modul_details(titel_suche: str) -> str:
    """
    Liefert Deails zu einem Modul, das über den Titel gesucht wird
    """

    conn = get_connection()
    if not conn:
        return "Verbindung zur Datenbank fehlgeschlagen"

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT modulnummer, titel, cp, sws, turnus, verantwortlich, fachsemester FROM module
            WHERE LOWER(titel) LIKE %s
            LIMIT 1
        """, ('%' + titel_suche.lower() + '%',))
        result = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not result:
        return f"Kein Modul gefunden, das zu '{titel_suche}' passt."

    modulnummer, titel, cp, sws, turnus, verantwortlich, fachsemester = result

    return (
        f"Modul {titel} ({modulnummer}):\n"
        f"- Credits: {cp}\n"
        f"- SWS: {sws}\n"
        f"- Turnus: {turnus}\n"
        f"- Verantwortlich: {verantwortlich}\n"
        f"- Fachsemester: {fachsemester}"
    )

if __name__ == "__main__":
    mcp.run(transport="stdio")
    #mcp.run(transport="http")

