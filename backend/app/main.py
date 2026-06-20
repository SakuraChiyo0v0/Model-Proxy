from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine, Base, SessionLocal
from app.models.route import RouteModel  # noqa: F401  ensure table creation
from app.api.proxy import router as proxy_router
from app.api.admin import router as admin_router
from app.config import settings
from app.repository.user_repo import UserRepo


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _migrate_db()
    _init_admin()
    yield


def _migrate_db():
    """对已有表添加新列（SQLite 不支持 ALTER TABLE ADD COLUMN IF NOT EXISTS，用 try/except）"""
    migrations = [
        "ALTER TABLE providers ADD COLUMN models_path VARCHAR(256)",
        "ALTER TABLE providers ADD COLUMN balance_path VARCHAR(256)",
        "ALTER TABLE users ADD COLUMN token VARCHAR(128)",
        "ALTER TABLE routes ADD COLUMN model VARCHAR(128) DEFAULT ''",
    ]
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"[MIGRATE] {sql.split('ADD COLUMN ')[1]}")
            except Exception:
                pass  # 列已存在，忽略


def _init_admin():
    db = SessionLocal()
    try:
        repo = UserRepo(db)
        if not repo.get_by_username(settings.admin_username):
            repo.create(settings.admin_username, settings.admin_password)
            print(f"[INIT] Admin user '{settings.admin_username}' created")
    finally:
        db.close()


app = FastAPI(title="Model Proxy", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(proxy_router)
app.include_router(admin_router)
