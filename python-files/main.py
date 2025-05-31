from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/io_log")
async def io_log(request: Request):
    data = await request.json()
    print("Received data:", data)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
