# basic_01.py - FastAPI App đầu tiên
from fastapi import FastAPI # type: ignore

# Tạo một instance của FastAPI
app = FastAPI()

# Endpoint đơn giản nhất
@app.get("/")
def read_root():
    return {"message": "Xin chào! Đây là FastAPI app đầu tiên của tôi"}

# Chạy server
if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)