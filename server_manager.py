#!/usr/bin/env python3

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

class ServerManager:
    def __init__(self):
        self.app_name = "geoip-api"
        self.app_file = "app.py"
        self.pid_file = f"{self.app_name}.pid"
        self.log_file = f"{self.app_name}.log"
    
    def get_pid(self):
        """Get PID from PID file"""
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    return int(f.read().strip())
            except (ValueError, FileNotFoundError):
                return None
        return None
    
    def is_running(self, pid=None):
        """Check if process is running"""
        if pid is None:
            pid = self.get_pid()
        
        if pid is None:
            return False
        
        try:
            os.kill(pid, 0)  # Send signal 0 to check if process exists
            return True
        except (OSError, ProcessLookupError):
            return False
    
    def start(self):
        """Start the server in background"""
        pid = self.get_pid()
        if pid and self.is_running(pid):
            print(f"Server is already running (PID: {pid})")
            return False
        
        print(f"Starting {self.app_name} server...")
        
        # Start the process
        with open(self.log_file, 'w') as log:
            process = subprocess.Popen(
                [sys.executable, self.app_file],
                stdout=log,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid  # Create new session
            )
        
        # Save PID
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        
        # Wait a moment to check if it started successfully
        time.sleep(2)
        if self.is_running(process.pid):
            print(f"Server started successfully (PID: {process.pid})")
            print(f"Log file: {self.log_file}")
            return True
        else:
            print("Failed to start server")
            self.cleanup()
            return False
    
    def stop(self):
        """Stop the server"""
        pid = self.get_pid()
        if not pid:
            print("Server is not running")
            return False
        
        if not self.is_running(pid):
            print("Server is not running (stale PID file)")
            self.cleanup()
            return False
        
        print(f"Stopping {self.app_name} server (PID: {pid})...")
        
        try:
            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to terminate
            for _ in range(10):  # Wait up to 10 seconds
                if not self.is_running(pid):
                    break
                time.sleep(1)
            
            # Force kill if still running
            if self.is_running(pid):
                print("Forcing shutdown...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
            
            self.cleanup()
            print("Server stopped")
            return True
            
        except (OSError, ProcessLookupError):
            print("Error stopping server")
            self.cleanup()
            return False
    
    def restart(self):
        """Restart the server"""
        print("Restarting server...")
        self.stop()
        time.sleep(2)
        return self.start()
    
    def status(self):
        """Check server status"""
        pid = self.get_pid()
        if pid and self.is_running(pid):
            print(f"Server is running (PID: {pid})")
            return True
        else:
            print("Server is not running")
            self.cleanup()
            return False
    
    def logs(self):
        """Show server logs"""
        if os.path.exists(self.log_file):
            try:
                # Use tail -f equivalent
                subprocess.run(['tail', '-f', self.log_file])
            except KeyboardInterrupt:
                print("\nLog monitoring stopped")
        else:
            print("Log file not found")
    
    def cleanup(self):
        """Clean up PID file"""
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 server_manager.py {start|stop|restart|status|logs}")
        print("")
        print("Commands:")
        print("  start   - Start the server in background")
        print("  stop    - Stop the server")
        print("  restart - Restart the server")
        print("  status  - Check server status")
        print("  logs    - Show server logs (tail -f)")
        sys.exit(1)
    
    manager = ServerManager()
    command = sys.argv[1].lower()
    
    if command == 'start':
        manager.start()
    elif command == 'stop':
        manager.stop()
    elif command == 'restart':
        manager.restart()
    elif command == 'status':
        manager.status()
    elif command == 'logs':
        manager.logs()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main() 