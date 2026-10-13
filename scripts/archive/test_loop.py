import urllib.request, time

for i in range(10):
    try:
        req = urllib.request.Request("http://127.0.0.1:8001/api/simulation/state")
        with urllib.request.urlopen(req) as response:
            print("200 OK")
    except Exception as e:
        print("Error:", e)
    time.sleep(1)
