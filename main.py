from fastapi import FastAPI
from pydantic import BaseModel
from notion_handler import add_entry, read_entries, update_entry, delete_entry
import uvicorn

app = FastAPI(
    title="GPT-Notion Backend",
    description="Acciones CRUD unificadas para las cuatro bases de datos",
    version="1.0.0"
)

# ---------- Pydantic schema para entrada ----------
class Entrada(BaseModel):
    action: str     # add, read, update, delete
    tipo: str       # tarea, reflexion, recurso, deseo
    data: dict | None = None        # requerido en add / update
    page_id: str | None = None      # requerido en update / delete
    filter_payload: dict | None = None  # opcional en read


@app.post("/entrada")
def procesar_entrada(entrada: Entrada):
    """
    Recibe un JSON del GPT y ejecuta la acción pedida.
    """
    try:
        if entrada.action == "add":
            return add_entry(entrada.tipo, entrada.data or {})

        elif entrada.action == "read":
            return read_entries(entrada.tipo, entrada.filter_payload)

        elif entrada.action == "update":
            if not entrada.page_id:
                return {"error": "page_id requerido para update"}
            return update_entry(entrada.page_id, entrada.data or {})

        elif entrada.action == "delete":
            if not entrada.page_id:
                return {"error": "page_id requerido para delete"}
            return delete_entry(entrada.page_id)

        else:
            return {"error": "Acción no reconocida"}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
