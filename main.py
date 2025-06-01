from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from notion_handler import add_entry, read_entries, update_entry, delete_entry

app = FastAPI()

@app.post("/entrada")
async def handle_entry(request: Request):
    try:
        body = await request.json()
        action = body.get("action")
        tipo = body.get("tipo")
        data = body.get("data", {})

        if action == "add":
            return add_entry(tipo, data)

        elif action == "read":
            return read_entries(tipo)

        elif action == "update":
            page_id = data.get("page_id")
            properties = data.get("properties", {})
            if not page_id:
                return JSONResponse(content={"error": "Falta page_id para actualizar."}, status_code=400)
            return update_entry(page_id, properties)

        elif action == "delete":
            page_id = data.get("page_id")
            if not page_id:
                return JSONResponse(content={"error": "Falta page_id para eliminar."}, status_code=400)
            return delete_entry(page_id)

        else:
            return JSONResponse(content={"error": f"Acción '{action}' no reconocida."}, status_code=400)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
def home():
    return {"status": "Servidor activo y funcionando 🚀"}
