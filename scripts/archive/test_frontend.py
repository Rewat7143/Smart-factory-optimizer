import urllib.request
try:
    with urllib.request.urlopen("http://localhost:3005", timeout=5) as response:
        print("STATUS:", response.status)
except Exception as e:
    print("FAILED:", e)
