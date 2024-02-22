from fastapi import FastAPI

app = FastAPI()


@app.get('/get/')
async def root():
    return {"message": "Hello World"}
