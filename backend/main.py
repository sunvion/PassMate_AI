from fastapi import FastAPI

app = FastAPI(title="PassCertificate - API Server")

@app.get("/")
async def root():
    return {"message": "Welcome to PassCertificate Backend API Server"}