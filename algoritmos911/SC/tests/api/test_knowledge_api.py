import pytest
from httpx import AsyncClient
from sc.main import app # Убедитесь, что это правильный импорт вашего FastAPI приложения

# Фикстура для создания асинхронного клиента для каждого теста
@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        yield ac

@pytest.mark.asyncio
async def test_read_docs(client: AsyncClient):
    """
    Тест для проверки доступности Swagger UI (документации API).
    """
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

@pytest.mark.asyncio
async def test_upload_vr_endpoint_exists(client: AsyncClient):
    """
    Тест для проверки, что эндпоинт /api/knowledge/upload_vr существует
    и отвечает корректно на OPTIONS запрос (обычно используется для CORS preflight).
    Или просто что он не возвращает 404 на POST без данных.
    Для более полного теста нужны данные формы.
    """
    # Проверим, что путь зарегистрирован, отправив POST без данных.
    # Ожидаем 422 Unprocessable Entity, так как данные формы отсутствуют,
    # но это подтверждает, что эндпоинт существует.
    response = await client.post("/api/knowledge/upload_vr")
    assert response.status_code == 422 # Unprocessable Entity (из-за отсутствия Form данных)
    # Если бы эндпоинт не существовал, был бы 404.
    # Проверим, что в ответе есть JSON (стандартный ответ FastAPI для ошибок валидации)
    assert "application/json" in response.headers["content-type"]
    json_response = response.json()
    assert "detail" in json_response # FastAPI обычно включает поле "detail" в ошибки валидации
    # Проверяем, что ошибка связана с отсутствующими полями формы
    missing_fields_details = [item['type'] == 'missing' for item in json_response['detail']]
    assert any(missing_fields_details)

# Чтобы этот тест можно было запустить напрямую (хотя обычно используется pytest)
if __name__ == "__main__":
    pytest.main([__file__])
