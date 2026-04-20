from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ProductSchema(BaseModel):
    seo_title: str
    price: int
    category: str

@app.post("/api/v1/internal/register")
async def mock_register(item: ProductSchema):
    print(f"📦 [API 수신] 상품명: {item.seo_title} / 가격: {item.price}")
    return {"status": "success", "message": "ERP 시스템 등록 완료"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)