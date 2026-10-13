import urllib.request
try:
    req = urllib.request.Request("http://127.0.0.1:8001/api/simulation/state")
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except Exception as e:
    print("Error:", e)
