#!/usr/bin/env python3
"""
Run the Write Proofread Software Web Interface
"""

from web_interface import app

if __name__ == '__main__':
    print("Starting Write Proofread Software Web Interface...")
    print("Access the interface at http://localhost:5000")
    app.run(debug=True, port=5000)