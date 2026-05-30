#!/bin/bash

# Configuration
APP_NAME="Flask Bookmark Directory"
APP_CMD="python url_directory.py"   # <-- changed to your actual file
PID_FILE="./flask_app.pid"          # <-- store PID in current folder

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

start() {
    if is_running; then
        echo -e "${YELLOW}$APP_NAME is already running (PID: $(cat $PID_FILE))${NC}"
    else
        echo -e "${GREEN}Starting $APP_NAME...${NC}"
        nohup $APP_CMD > flask_output.log 2>&1 &   # <-- save output for debugging
        echo $! > "$PID_FILE"
        sleep 2
        if is_running; then
            echo -e "${GREEN}Started with PID: $(cat $PID_FILE)${NC}"
        else
            echo -e "${RED}Failed to start $APP_NAME. Check flask_output.log${NC}"
            rm -f "$PID_FILE"
        fi
    fi
}

stop() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}Stopping $APP_NAME (PID: $PID)...${NC}"
        kill "$PID"
        for i in {1..5}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${RED}Force killing...${NC}"
            kill -9 "$PID"
            sleep 1
        fi
        rm -f "$PID_FILE"
        echo -e "${GREEN}Stopped.${NC}"
    else
        echo -e "${YELLOW}$APP_NAME is not running.${NC}"
    fi
}

restart() {
    stop
    start
}

status() {
    if is_running; then
        echo -e "${GREEN}$APP_NAME is running (PID: $(cat $PID_FILE))${NC}"
    else
        echo -e "${YELLOW}$APP_NAME is not running.${NC}"
    fi
}

pid() {
    if is_running; then
        cat "$PID_FILE"
    else
        echo "Not running"
    fi
}

case "$1" in
    start)   start ;;
    stop)    stop ;;
    restart) restart ;;
    status)  status ;;
    pid)     pid ;;
    *)       echo "Usage: $0 {start|stop|restart|status|pid}" ;;
esac