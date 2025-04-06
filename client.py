import sys

import requests


def send_request():
    """send fake data to backend to test the update functionality"""
    payload = f"UIDresult=1234"
    json_data = {"UIDresult": "1234"}
    response = requests.post(
        "http://213.6.135.126:8000/api/arduino",
        data=payload,
        json=json_data,
        verify=False,
    )
    if response.status_code == 200:
        print("data updated successfully")
    else:
        print("Error while sending request", response.reason)


send_request()
