#!/bin/bash
# =============================================================================
# Start All Services - HF Virtual Stylist (Mac/Linux)
# =============================================================================

echo ""
echo "========================================================================"
echo "  HF Virtual Stylist - Starting All Services"
echo "========================================================================"
echo ""
echo "This will open 3 terminal tabs/windows:"
echo "  1. Backend API (port 8000)"
echo "  2. Worker (processes generation jobs)"
echo "  3. Frontend (port 3000)"
echo ""
echo "Press Ctrl+C in each terminal to stop the services."
echo "========================================================================"
echo ""

# Get the script directory (project root)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Detect OS for terminal opening
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use iTerm2 or Terminal.app
    echo "[1/3] Starting Backend API..."
    osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR/backend' && source venv/bin/activate && echo '' && echo '======================================' && echo '  Backend API Starting...' && echo '======================================' && echo '' && uvicorn app.main:app --reload --port 8000"
end tell
EOF

    sleep 2

    echo "[2/3] Starting Worker..."
    osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR/backend' && source venv/bin/activate && echo '' && echo '======================================' && echo '  Worker Starting...' && echo '======================================' && echo '' && python worker.py"
end tell
EOF

    sleep 2

    echo "[3/3] Starting Frontend..."
    osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR/frontend' && echo '' && echo '======================================' && echo '  Frontend Starting...' && echo '======================================' && echo '' && npm run dev"
end tell
EOF

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - use gnome-terminal, xterm, or konsole
    if command -v gnome-terminal &> /dev/null; then
        TERM_CMD="gnome-terminal --tab"
    elif command -v konsole &> /dev/null; then
        TERM_CMD="konsole --new-tab -e"
    elif command -v xterm &> /dev/null; then
        TERM_CMD="xterm -e"
    else
        echo "Error: No compatible terminal found (gnome-terminal, konsole, xterm)"
        exit 1
    fi

    echo "[1/3] Starting Backend API..."
    $TERM_CMD bash -c "cd '$PROJECT_DIR/backend' && source venv/bin/activate && echo '' && echo '======================================' && echo '  Backend API Starting...' && echo '======================================' && echo '' && uvicorn app.main:app --reload --port 8000; exec bash" &

    sleep 2

    echo "[2/3] Starting Worker..."
    $TERM_CMD bash -c "cd '$PROJECT_DIR/backend' && source venv/bin/activate && echo '' && echo '======================================' && echo '  Worker Starting...' && echo '======================================' && echo '' && python worker.py; exec bash" &

    sleep 2

    echo "[3/3] Starting Frontend..."
    $TERM_CMD bash -c "cd '$PROJECT_DIR/frontend' && echo '' && echo '======================================' && echo '  Frontend Starting...' && echo '======================================' && echo '' && npm run dev; exec bash" &

else
    echo "Error: Unsupported OS: $OSTYPE"
    exit 1
fi

echo ""
echo "========================================================================"
echo "  All services started!"
echo "========================================================================"
echo ""
echo "  Backend API:  http://localhost:8000/docs"
echo "  Frontend:     http://localhost:3000"
echo ""
echo "  Check each terminal for status."
echo "  To stop: Close the terminals or press Ctrl+C in each."
echo "========================================================================"
echo ""
