from fastapi import FastAPI



app = FastAPI(
    title="ARHEA API",
    version="0.1.0",
    debug=True,
)


@app.get("/")
async def check():
    return {"status": "ok"}