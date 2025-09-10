from fastapi import FastAPI
from users import router as users_router
app = FastAPI()

@app.get("/hello")
def read_hello():
    return {"message": "hello"}

app.include_router(users_router)
