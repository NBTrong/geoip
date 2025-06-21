#!/bin/bash

# GeoIP API Background Server Script

APP_NAME="geoip-api"
APP_FILE="app.py"
PID_FILE="$APP_NAME.pid"
LOG_FILE="$APP_NAME.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            echo "Server is already running (PID: $(cat $PID_FILE))"
            exit 1
        fi
        
        echo "Starting $APP_NAME server..."
        nohup python3 "$APP_FILE" > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "Server started with PID: $(cat $PID_FILE)"
        echo "Log file: $LOG_FILE"
        ;;
    
    stop)
        if [ ! -f "$PID_FILE" ]; then
            echo "Server is not running"
            exit 1
        fi
        
        PID=$(cat "$PID_FILE")
        echo "Stopping $APP_NAME server (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "Server stopped"
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "Server is running (PID: $PID)"
            else
                echo "Server is not running (stale PID file)"
                rm -f "$PID_FILE"
            fi
        else
            echo "Server is not running"
        fi
        ;;
    
    logs)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "Log file not found"
        fi
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the server in background"
        echo "  stop    - Stop the server"
        echo "  restart - Restart the server"
        echo "  status  - Check server status"
        echo "  logs    - Show server logs (tail -f)"
        exit 1
        ;;
esac 