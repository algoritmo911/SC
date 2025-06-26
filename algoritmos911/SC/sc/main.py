# sc/main.py
from fastapi import FastAPI
from sc.api import knowledge # Оставим пока так, pytest должен справиться при правильном PYTHONPATH

app = FastAPI(
    title="Sapiens Coin Platform",
    description="Децентрализованная фабрика памяти и ценности знаний",
    version="0.1.0"
)

# Подключаем маршруты
app.include_router(knowledge.router, prefix="/api/knowledge")
