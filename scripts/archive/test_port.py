import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(("127.0.0.1", 8000))
    print("Port 8000 is open!")
    s.sendall(b"GET /api/simulation/state HTTP/1.1\r\nHost: 127.0.0.1:8000\r\n\r\n")
    print(s.recv(1024).decode())
except Exception as e:
    print("Port 8000 is closed or error:", e)
finally:
    s.close()
