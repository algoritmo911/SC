# sc/services/ipfs_service.py

from uuid import uuid4
from fastapi import UploadFile
import shutil
import os

# Временная директория для "mock" IPFS хранилища
MOCK_IPFS_STORAGE_PATH = ".mock_ipfs_storage"
os.makedirs(MOCK_IPFS_STORAGE_PATH, exist_ok=True)

class IPFSService:
    async def add_file(self, file: UploadFile) -> str:
        """
        Симулирует добавление файла в IPFS.
        В реальности здесь будет вызов IPFS API (например, через ipfshttpclient).
        Возвращает "IPFS хеш" (в данном случае это имя файла).
        """
        # Генерируем уникальное имя файла для симуляции хеша
        # В реальном IPFS хеш будет другим
        file_extension = os.path.splitext(file.filename)[1]
        mock_ipfs_hash = f"QmSimulated{uuid4().hex}{file_extension}"
        file_path = os.path.join(MOCK_IPFS_STORAGE_PATH, mock_ipfs_hash)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            file.file.close() # Убедимся, что файл закрыт

        return mock_ipfs_hash

    async def get_file_content(self, ipfs_hash: str) -> bytes:
        """
        Симулирует получение файла из IPFS.
        В реальности здесь будет вызов IPFS API.
        """
        file_path = os.path.join(MOCK_IPFS_STORAGE_PATH, ipfs_hash)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File with hash {ipfs_hash} not found in mock IPFS storage.")

        with open(file_path, "rb") as f:
            return f.read()

    async def add_json(self, data: dict) -> str:
        """
        Симулирует добавление JSON-объекта в IPFS.
        """
        import json
        mock_ipfs_hash = f"QmSimulatedJson{uuid4().hex}.json"
        file_path = os.path.join(MOCK_IPFS_STORAGE_PATH, mock_ipfs_hash)

        with open(file_path, "w") as f:
            json.dump(data, f)

        return mock_ipfs_hash

# Экземпляр сервиса для использования в приложении
ipfs_service = IPFSService()

async def get_ipfs_service():
    return ipfs_service

# Пример использования (можно удалить или закомментировать)
if __name__ == "__main__":
    import asyncio

    async def test_ipfs_service():
        service = IPFSService()

        # Создаем фейковый UploadFile для теста
        class MockUploadFile:
            def __init__(self, filename, content, content_type="text/plain"):
                self.filename = filename
                self.file = open(filename, "wb+") # Открываем в wb+ для записи и чтения
                self.file.write(content.encode())
                self.file.seek(0) # Возвращаем курсор в начало файла
                self.content_type = content_type

            async def read(self):
                return self.file.read()

            async def close(self):
                self.file.close()
                os.remove(self.filename) # Удаляем временный файл

        # Тест добавления файла
        mock_file_content = "Это тестовое содержимое для IPFS!"
        mock_file_name = "test_upload.txt"

        # Создаем временный файл для UploadFile
        with open(mock_file_name, "w") as f:
            f.write(mock_file_content)

        # Открываем файл в бинарном режиме для UploadFile
        with open(mock_file_name, "rb") as f_rb:
            upload_file_obj = UploadFile(filename=mock_file_name, file=f_rb)

            print(f"Testing add_file with {mock_file_name}...")
            try:
                added_hash = await service.add_file(upload_file_obj)
                print(f"File added to mock IPFS, hash: {added_hash}")

                # Тест получения файла
                print(f"Testing get_file_content for hash: {added_hash}...")
                retrieved_content = await service.get_file_content(added_hash)
                print(f"Retrieved content: {retrieved_content.decode()}")
                assert retrieved_content.decode() == mock_file_content
                print("File content matches!")
            except Exception as e:
                print(f"Error during file test: {e}")
            finally:
                # UploadFile сам закроет файл, если он был передан как file-like объект
                # но если мы создавали его вручную, нужно убедиться в закрытии
                # и удалении временного файла, если он больше не нужен
                if os.path.exists(mock_file_name):
                    os.remove(mock_file_name)


        # Тест добавления JSON
        mock_json_data = {"name": "KnowledgeUnit", "version": "1.0"}
        print(f"\nTesting add_json with data: {mock_json_data}...")
        try:
            json_hash = await service.add_json(mock_json_data)
            print(f"JSON added to mock IPFS, hash: {json_hash}")

            # Тест получения JSON (симуляция)
            print(f"Testing get_file_content for JSON hash: {json_hash}...")
            retrieved_json_bytes = await service.get_file_content(json_hash)
            import json
            retrieved_json_data = json.loads(retrieved_json_bytes.decode())
            print(f"Retrieved JSON data: {retrieved_json_data}")
            assert retrieved_json_data == mock_json_data
            print("JSON data matches!")
        except Exception as e:
            print(f"Error during JSON test: {e}")

        # Очистка mock хранилища после тестов (опционально)
        # print("\nCleaning up mock IPFS storage...")
        # for item in os.listdir(MOCK_IPFS_STORAGE_PATH):
        #     os.remove(os.path.join(MOCK_IPFS_STORAGE_PATH, item))
        # os.rmdir(MOCK_IPFS_STORAGE_PATH) # Удаляем саму директорию
        # print("Mock IPFS storage cleaned.")


    asyncio.run(test_ipfs_service())
