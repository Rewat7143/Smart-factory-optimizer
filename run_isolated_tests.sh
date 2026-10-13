source backend/.venv/bin/activate

run_test() {
    pkill -f uvicorn
    sleep 1
    cd backend
    python3 main.py &
    SERVER_PID=$!
    sleep 4
    cd ..
    python3 test_forecast_final.py $1
    pkill -f uvicorn
    sleep 2
}

run_test short
run_test long
run_test missing
run_test future
