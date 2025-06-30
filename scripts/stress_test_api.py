import asyncio
import httpx
import time
import csv
import os
from uuid import uuid4

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"  # Assuming the FastAPI app runs on port 8000
NUM_REQUESTS = 100
CONCURRENT_REQUESTS = 100  # Number of requests to send in parallel

ENDPOINTS = [
    {"method": "GET", "path": "/knowledge/"},
    {"method": "POST", "path": "/knowledge/upload_vr"},
    {"method": "GET", "path": "/users/"},
    {"method": "POST", "path": "/users/"},
    {"method": "GET", "path": "/tokens/"},
    {"method": "POST", "path": "/tokens/"},
]

RESULTS_FILE = "api_stress_results.csv"
DUMMY_FILE_CONTENT = b"This is a dummy VR scene file."
DUMMY_FILE_NAME = "dummy_scene.dat"

async def make_request(client, endpoint_config, results):
    method = endpoint_config["method"]
    url = BASE_URL + endpoint_config["path"]
    start_time = time.time()
    error = None
    status_code = None
    response_data = None

    try:
        if method == "GET":
            response = await client.get(url, timeout=30.0)
        elif method == "POST":
            if endpoint_config["path"] == "/knowledge/upload_vr":
                files = {"vr_scene": (DUMMY_FILE_NAME, DUMMY_FILE_CONTENT, "application/octet-stream")}
                data = {
                    "author_id": str(uuid4()),
                    "tags": "vr,test,dummy"
                }
                response = await client.post(url, data=data, files=files, timeout=30.0)
            else:
                response = await client.post(url, json={"test_data": "some_value"}, timeout=30.0)

        status_code = response.status_code
        response_data = response.text
        response.raise_for_status()  # Raise an exception for bad status codes
    except httpx.RequestError as exc:
        error = str(exc)
        if hasattr(exc, 'response') and exc.response is not None:
            status_code = exc.response.status_code
    except Exception as exc:
        error = str(exc)

    end_time = time.time()
    response_time = end_time - start_time

    results.append({
        "timestamp": time.time(),
        "endpoint": endpoint_config["path"],
        "method": method,
        "status_code": status_code,
        "response_time_seconds": response_time,
        "error": error,
        # "response_data": response_data # Optional: log response data
    })

async def main():
    # Create a dummy file for uploads
    with open(DUMMY_FILE_NAME, "wb") as f:
        f.write(DUMMY_FILE_CONTENT)

    results = []
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(NUM_REQUESTS // len(ENDPOINTS)): # Distribute requests among endpoints
            for endpoint_config in ENDPOINTS:
                tasks.append(make_request(client, endpoint_config, results))

        # Ensure exactly NUM_REQUESTS are made, distribute remaining if any
        remaining_requests = NUM_REQUESTS % len(ENDPOINTS)
        for i in range(remaining_requests):
            tasks.append(make_request(client, ENDPOINTS[i % len(ENDPOINTS)], results))

        # Limit concurrency
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
        async def run_with_semaphore(task):
            async with semaphore:
                await task

        await asyncio.gather(*(run_with_semaphore(task) for task in tasks))

    # Clean up dummy file
    if os.path.exists(DUMMY_FILE_NAME):
        os.remove(DUMMY_FILE_NAME)

    # Write results to CSV
    if results:
        with open(RESULTS_FILE, "w", newline="") as csvfile:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Stress test complete. Results saved to {RESULTS_FILE}")
    else:
        print("No results to save.")

if __name__ == "__main__":
    asyncio.run(main())
