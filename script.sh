#!/bin/bash

# function to check if a container is running
check_container() {
    if podman ps | grep -q $1; then
        echo "$1 is running."
        return 0
    else
        echo "$1 is not running. Starting..."
        podman start $1
        if [ $? -ne 0 ]; then
            echo "Failed to start $1"
            return 1
        fi
        echo "$1 started successfully."
        return 0
    fi
}

# function to check if a port is in use
check_port() {
    if netstat -tuln | grep -q :$1; then
        echo "Port $1 is in use."
        return 0
    else
        echo "Port $1 is not in use."
        return 1
    fi
}

# main script
case "$1" in
    start)
        echo "Starting DocsBotIG service..."

        # check and start containers
        check_container "docsbotqdrant" || exit 1
        check_container "docsbotredis" || exit 1
        check_container "docsbotpostgres" || exit 1

        # check if containers are listening on their ports
        sleep 5  # Give containers time to start up
        check_port 6334 || exit 1
        check_port 6379 || exit 1
        check_port 5432 || exit 1

        # check if port 8000 is free
        if check_port 8000; then
            echo "Port 8000 is already in use. Exiting."
            exit 1
        fi

        # start the Python application with logging
        cd /home/cloud-user/intelligence_stage
        source docsbotig/bin/activate
        LOG_FILE="/home/cloud-user/intelligence_stage/docsbot.log"
        export PROFILE=production
        nohup python main.py > "$LOG_FILE" 2>&1 &
        echo $! > /tmp/docsbot.pid
        echo "DocsBotIG service started. Logs are being written to $LOG_FILE"
        ;;

    stop)
        echo "Stopping DocsBotIG service..."
        if pgrep -f "python.*main\.py" > /dev/null; then
            pkill -f "python.*main\.py"
            echo "Python application stopped."
        else
            echo "Python application was not running."
        fi
        podman stop docsbotqdrant docsbotredis docsbotpostgres
        ;;

    status)
        echo "Checking DocsBotIG service status..."
        check_container "docsbotqdrant"
        check_container "docsbotredis"
        check_container "docsbotpostgres"
        check_port 6334
        check_port 6379
        check_port 5432
        check_port 8000
        if pgrep -f "python.*main\.py" > /dev/null; then
            pid=$(pgrep -f "python.*main\.py")
            echo "Python application is running with PID $pid."
        else
            echo "Python application is not running."
        fi
        ;;

    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac

exit 0