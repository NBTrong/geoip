import geoip2.database
import time
from flask import Flask, jsonify, request
import geoip2.errors
import os
import threading
import requests
from datetime import datetime

# URL to download the latest GeoLite2 City database
DB_URL = "https://git.io/GeoLite2-City.mmdb"
# Local filename for the database
DB_FILE = "GeoLite2-City.mmdb"

# How often to refresh the DB (in seconds)
REFRESH_INTERVAL = 24 * 60 * 60  # 1 day

app = Flask(__name__)

def local_ip_lookup(ip):
    with geoip2.database.Reader('GeoLite2-City.mmdb') as reader:
        response = reader.city(ip)
        return {
            "city": response.city.name,
            "country": response.country.name,
            "latitude": response.location.latitude,
            "longitude": response.location.longitude
        }

@app.route('/lookup/<ip>')
def lookup_ip(ip):
    """Lookup IP address information"""
    try:
        start_time = time.time()
        result = local_ip_lookup(ip)
        end_time = time.time()
        
        result["lookup_time_ms"] = round((end_time - start_time) * 1000, 2)
        result["ip"] = ip
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except geoip2.errors.AddressNotFoundError:
        return jsonify({
            "success": False,
            "error": "IP address not found in database"
        }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ---------------------------
# Database update utilities
# ---------------------------

def download_latest_db():
    """Download the latest GeoLite2-City database and replace the existing file."""
    try:
        print(f"[{datetime.utcnow().isoformat()}] Downloading latest GeoLite2 database...")
        response = requests.get(DB_URL, timeout=3600)
        response.raise_for_status()

        tmp_path = DB_FILE + ".tmp"
        with open(tmp_path, "wb") as f:
            f.write(response.content)

        # Atomically replace the old database
        os.replace(tmp_path, DB_FILE)
        print(f"[{datetime.utcnow().isoformat()}] Database updated successfully.")

    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] Failed to update GeoLite2 database: {e}")


def schedule_db_updates():
    """Start a background daemon thread that updates the DB once per day."""

    def _run():
        # Run immediately at startup
        download_latest_db()
        while True:
            time.sleep(REFRESH_INTERVAL)
            download_latest_db()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    print("Started GeoLite2 auto-update thread.")

# ---------------------------

if __name__ == '__main__':
    # Test the function first
    print("Testing IP lookup...")
    start_time = time.time()
    result = local_ip_lookup("116.96.47.227")
    end_time = time.time()
    print(result)
    print(f"Lookup took: {(end_time - start_time) * 1000:.2f} ms")
    
    # Start auto-update background thread
    schedule_db_updates()
    
    # Start Flask app
    print("\nStarting Flask API server...")
    app.run(debug=True, host='0.0.0.0', port=80)
