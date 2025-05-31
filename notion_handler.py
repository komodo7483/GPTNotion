import os
import requests
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

# IDs de bases sacados del .env
DATABASES = {
    "tarea": os.getenv("DATABASE_ID_TAREAS"),
    "reflexion": os.getenv("DATABASE_ID_REFLEXIONES"),
    "recurso": os.getenv("DATABASE_ID_BIBLIOTECA"),
    "deseo":   os.getenv("DATABASE_ID_DESEOS")
}

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}


# ---------- HELPERS -------------------------------------------------
def _notion_post(url: str, payload: dict):
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()

def _notion_patch(page_id: str, payload: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    resp = requests.patch(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()


# ---------- CREATE --------------------------------------------------
def add_entry(tipo: str, data: dict):
    """
    Crea una página en la base indicada por 'tipo' con los campos de 'data'.
    """
    db_id = DATABASES.get(tipo)
    if not db_id:
        return {"error": f"Tipo {tipo} no soportado o DB_ID no definido."}

    # -------- payload por tipo ----------
    if tipo == "tarea":
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "Short":   {"title":  [{"text": {"content": data["short"]}}]},
                "Select":  {"select": {"name": data.get("select", "PUFF")}},
                "End Date": (
                    {"date": {"start": data["end_date"]}}
                    if data.get("end_date") else {"date": None}
                )
            },
            "children": [
                _rich_paragraph(data.get("descripcion", ""))
            ]
        }

    elif tipo == "reflexion":
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "Short":   {"title":     [{"text": {"content": data["short"]}}]},
                "Summary": {"rich_text": [{"text": {"content": data["summary"]}}]},
                "Date":    {"date":      {"start": data.get("date", _today())}}
            },
            "children": [_rich_paragraph(data.get("contenido", ""))]
        }

    elif tipo == "recurso":
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "Short": {"title": [{"text": {"content": data["short"]}}]},
                "Links": {"url": data.get("links", "")},
                "Full":  {"rich_text": [{"text": {"content": data.get("full", "")}}]}
            }
        }

    elif tipo == "deseo":
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "Short": {"title": [{"text": {"content": data["short"]}}]},
                "Why?":  {"rich_text": [{"text": {"content": data.get("why", "")}}]}
            }
        }

    else:
        return {"error": "Tipo no reconocido"}

    return _notion_post("https://api.notion.com/v1/pages", payload)


# ---------- READ ----------------------------------------------------
def read_entries(tipo: str, filter_payload: dict | None = None):
    """
    Devuelve páginas de la base indicada por 'tipo'.
    Puedes pasar un filtro Notion API en filter_payload.
    """
    db_id = DATABASES.get(tipo)
    if not db_id:
        return {"error": f"Tipo {tipo} no soportado o DB_ID no definido."}

    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = filter_payload or {}
    return _notion_post(url, payload)


# ---------- UPDATE --------------------------------------------------
def update_entry(page_id: str, properties: dict):
    """
    Modifica una página concreta por ID (propiedades).
    'properties' debe seguir la spec de Notion.
    """
    return _notion_patch(page_id, {"properties": properties})


# ---------- DELETE (archivar) ---------------------------------------
def delete_entry(page_id: str):
    """
    Archiva la página (Notion no permite delete definitivo vía API).
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    return _notion_patch(page_id, {"archived": True})


# ---------- UTIL ----------------------------------------------------
def _today() -> str:
    return date.today().isoformat()

def _rich_paragraph(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": text}}
            ]
        }
    }
