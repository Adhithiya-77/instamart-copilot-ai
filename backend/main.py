from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import db_exists, DB_PATH
from backend.routes import dashboard, orders, products, customers, analytics, assistant, data_quality

app = FastAPI(title="Instamart Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(analytics.router)
app.include_router(assistant.router)
app.include_router(data_quality.router)


@app.get("/api/health")
def health():
    ok = db_exists()
    return {
        "status": "ok" if ok else "degraded",
        "database": "connected" if ok else "not found",
        "db_path": str(DB_PATH),
    }
