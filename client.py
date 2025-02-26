import sys

import requests


def send_request():
    """send fake data to backend to test the update functionality"""
    payload = f"UIDresult=111"
    json_data = {"UIDresult": "111"}
    response = requests.post(
        "http://127.0.0.1:8000/api/arduino", data=payload, json=json_data, verify=False
    )
    if response.status_code == 200:
        print("data updated successfully")
    else:
        print("Error while sending request", response.reason)


send_request()
