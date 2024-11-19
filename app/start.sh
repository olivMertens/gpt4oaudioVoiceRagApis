python3 -m gunicorn backend/app:create_app -b 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker & 
python3 -m uvicorn api/main:app --host 0.0.0.0 --port 8675 &
wait 