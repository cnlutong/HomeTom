import requests
import json
import uvicorn
import multiprocessing
import time
import os
import sys

# Base URL
BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing get_today_stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/executions/stats/today")
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

    print("\nTesting list_executions...")
    try:
        response = requests.get(f"{BASE_URL}/api/executions")
        if response.status_code == 200:
            data = response.json()
            print(f"Success. Got {len(data['items'])} items.")
            # print(json.dumps(data, indent=2))
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    test_endpoints()
