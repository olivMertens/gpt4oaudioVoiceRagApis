python3 -m gunicorn app:create_app -b 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker &
cd api && python3 -m uvicorn main:app --host 0.0.0.0 --port 8765 &
wait