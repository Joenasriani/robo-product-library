import requests

def safe_request(url, headers, payload):
    try:
        return requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=15  # shorter timeout
        )
    except Exception as e:
        return {"error": str(e)}
