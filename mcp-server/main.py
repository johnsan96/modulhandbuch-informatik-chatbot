from mcp.server.fastmcp import FastMCP
from db import get_connection
import httpx
import json

mcp = FastMCP("modulhandbuch")

# ---------------------------------
# sucht module nach gesuchtem Titel
# ---------------------------------

@mcp.tool()
def get_modul_details(titel_suche: str) -> str:
    """ Liefert Deails zu einem Modul, das über den Titel gesucht wird """

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

# -----------------------------------------------------------------------------
# sucht module nach Stichwort und weiteren Filtern wie Semestern, ECTS, Pflicht
# -----------------------------------------------------------------------------

@mcp.tool()
def query_modules(
    fachsemester: int = None,
    ects: int = None,
    pflichtmodul: bool = None,
    suchwort: str = None
) -> str:

    """Sucht Module anhand von Filtern wie Semester, ECTS, Pflicht oder Stichwort (im Titel oder Inhalten)."""

    conn = get_connection()
    if not conn:
        return "Verbindung zur DB fehlgeschlagen"
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT DISTINCT m.id, m.modulnummer, m.titel, m.cp, m.sws, m.fachsemester,
                        m.turnus, m.verantwortlich, m.pflichtmodul, 
        GROUP_CONCAT(i.inhalt SEPARATOR '; ') AS inhalte
        FROM module m
        LEFT JOIN modul_inhalte i ON m.id = i.modul_id
        WHERE 1=1
    """
    params = []

    if fachsemester is not None:
        sql += " AND m.fachsemester = %s"
        params.append(fachsemester)
    if ects is not None:
        sql += " AND m.cp = %s"
        params.append(ects)
    if pflichtmodul is not None:
        sql += " AND m.pflichtmodul = %s"
        params.append(pflichtmodul)
    if suchwort:
        sql += " AND (LOWER(m.titel) LIKE %s OR LOWER(i.inhalt) LIKE %s)"
        like = "%" + suchwort.lower() + "%"
        params.extend([like, like])
    
    sql += " GROUP BY m.id"

    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    if not results:
        return "Keine passenden Module gefunden."

    return json.dumps(results, ensure_ascii=False, indent=2)

# ------------------------------------------------------------
# sucht Literatur
# ------------------------------------------------------------

@mcp.tool()
def get_modul_extras(titel: str) -> str:
    """Liefert Inhalte, Kompetenzen, Medien und Literatur eines Moduls."""

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    data = {"inhalte": [], "kompetenzen": [], "medien": [], "literatur": []}
    
    # Erst Modul-ID über Titel bestimmen (case-insensitive)
    cursor.execute("SELECT id FROM module WHERE LOWER(titel) = %s", (titel.lower(),))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return f"Kein Modul mit Titel '{titel}' gefunden."

    modul_id = row["id"]

    # Inhalte
    cursor.execute("SELECT inhalt FROM modul_inhalte WHERE modul_id=%s", (modul_id,))
    data["inhalte"] = [row["inhalt"] for row in cursor.fetchall()]

    # Literatur
    cursor.execute("SELECT autor, titel, isbn, verlag, jahr FROM modul_literatur WHERE modul_id=%s", (modul_id,))
    data["literatur"] = cursor.fetchall()

    # Medien
    cursor.execute("SELECT medium FROM modul_medien WHERE modul_id=%s", (modul_id,))
    data["medien"] = [row["medium"] for row in cursor.fetchall()]

    # Kompetenzen
    cursor.execute("SELECT typ, kompetenztext FROM modul_kompetenzen WHERE modul_id=%s", (modul_id,))
    data["kompetenzen"] = cursor.fetchall()

    cursor.close()
    conn.close()

    return json.dumps(data, ensure_ascii=False, indent=2)

# ----------------------------------------------------------
# these are test-tools, and not belongs to the actual topic
# -----------------------------------------------------------

@mcp.tool()
async def get_all_users() -> list:
 """ Liefert Informationen zu Personen """

 async with httpx.AsyncClient() as client:
    response = await client.get("https://dummyjson.com/users")
    return response.json().get("users", [])

@mcp.tool()
async def get_user_info(name_or_email: str) -> str:
    """ Liefert genaue Informationen zu einer Person """

    async with httpx.AsyncClient() as client:
         res = await client.get("https://dummyjson.com/users")
         users = res.json().get("users", [])

    term = name_or_email.strip().lower()

    for user in users:
        email = user.get("email", "").lower()
        name = f"{user.get('firstName', '')} {user.get('lastName', '')}".lower()

        if term in email or term in name:
             return (
                 f"Name: {user['firstName']} {user['lastName']}\n"
                 f"E-Mail: {user['email']}\n"
             )
    return "Kein passender Nutzer gefunden."



# main call
if __name__ == "__main__":
    mcp.run(transport="stdio")
    #mcp.run(transport="http")

