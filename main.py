from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.post("/entrada")
async def recibir_entrada(request: Request):
    data = await request.json()
    print("🔔 Entrada recibida:")
    print(data)
    return JSONResponse(content={"status": "ok", "mensaje": "Entrada recibida correctamente"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
