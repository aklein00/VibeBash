#!/usr/bin/env python3
"""
Game Manager Server
Serves the dashboard and provides a live scan API endpoint.

Usage:
  python3 server.py           # Start on port 8080
  python3 server.py 8090      # Start on custom port
"""

import http.server
import json
import os
import sys

GAMEMANAGER_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GAMEMANAGER_DIR)

import scanner


class GameManagerHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=GAMEMANAGER_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/api/scan':
            self.handle_scan()
        else:
            super().do_GET()

    def handle_scan(self):
        try:
            scanned = scanner.scan_all()
            catalog = scanner.load_catalog()
            report = scanner.compare_with_catalog(scanned, catalog)

            response = {
                "scanned": scanned,
                "report": [],
                "summary": {"inSync": 0, "outOfSync": 0, "new": 0},
            }

            for item in report:
                entry = {
                    "name": item["name"],
                    "diffs": item["diffs"],
                    "isNew": item["catalogMatch"] is None,
                    "scanned": item["scanned"],
                }
                response["report"].append(entry)

                if item["catalogMatch"] is None:
                    response["summary"]["new"] += 1
                elif item["diffs"]:
                    response["summary"]["outOfSync"] += 1
                else:
                    response["summary"]["inSync"] += 1

            # Regenerate versions.json while we have fresh scan data
            scanner.generate_versions(scanned, catalog)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        # Suppress noisy request logging for static files, keep API logs
        if '/api/' in (args[0] if args else ''):
            super().log_message(format, *args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = http.server.HTTPServer(("", port), GameManagerHandler)
    print(f"Game Manager running at http://localhost:{port}")
    print(f"API: http://localhost:{port}/api/scan")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
