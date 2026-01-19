#!/bin/bash

# HomeTom Development Environment Start Script
# This script starts the Frontend, Backend, and Test API Server simultaneously.

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}          🚀 Starting HomeTom Dev Environment 🚀          ${NC}"
echo -e "${BLUE}============================================================${NC}"

# Function to handle cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down all services...${NC}"
    kill $FRONTEND_PID $BACKEND_PID $TEST_API_PID 2>/dev/null
    exit
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Kill stale processes on target ports
echo -e "${BLUE}Checking for stale processes...${NC}"
for port in 8000 8123 8080; do
    pid=$(lsof -t -i:$port)
    if [ ! -z "$pid" ]; then
        echo -e "Killing process $pid on port $port"
        kill -9 $pid 2>/dev/null
    fi
done

# 1. Start Mock Hardware API Server (Port 8123)
echo -e "${PURPLE}[1/3] Starting Mock Hardware API Server (Port 8123)...${NC}"
./venv/bin/python3 -m uvicorn test_API_server.main:app --port 8123 --reload > mock_api.log 2>&1 &
TEST_API_PID=$!

# 2. Start HomeTom Backend (Port 8000)
echo -e "${GREEN}[2/3] Starting HomeTom Backend (Port 8000)...${NC}"
# Wait a few seconds for the mock server to initialize
sleep 5
./venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > backend_dev.log 2>&1 &
BACKEND_PID=$!

# 3. Start Frontend (Vite)
echo -e "${BLUE}[3/3] Starting Frontend (Vite)...${NC}"
cd Front
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}All services are starting up!${NC}"
echo -e "  • Mock HA API: http://localhost:8123"
echo -e "  • HomeTom API: http://localhost:8000"
echo -e "  • Frontend:    http://localhost:8080"
echo -e "  • Logs:        backend_dev.log, mock_api.log, frontend.log"
echo -e "${BLUE}============================================================${NC}"
echo -e "Press Ctrl+C to stop all services."

# Wait for all background processes
wait
