python3 -m gunicorn app:create_app -b 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker
echo "Starting API Server with Uvicorn..."
# Start the API using Uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8765 &
# Wait for both background processes to finish
wait
