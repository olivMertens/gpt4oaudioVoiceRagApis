#!/bin/sh

. ./scripts/load_python_env.sh

echo ""
echo "Restoring frontend npm packages"
echo ""
cd app/frontend
npm install
if [ $? -ne 0 ]; then
    echo "Failed to restore frontend npm packages"
    exit $?
fi

echo ""
echo "Building frontend"
echo ""
npm audit fix
npm run build
if [ $? -ne 0 ]; then
    echo "Failed to build frontend"
    exit $?
fi

echo ""
echo "Starting backend"
echo ""
cd ../../
./.venv/bin/python app/backend/app.py &
if [ $? -ne 0 ]; then
    echo "Failed to start backend"
    exit $?
fi

echo ""
echo "Starting api"
echo ""
./.venv/bin/python app/api/main.py
if [ $? -ne 0 ]; then
    echo "Failed to start api"
    exit $?
fi
