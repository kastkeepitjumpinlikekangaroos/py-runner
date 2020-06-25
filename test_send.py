import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    code = b'''def a():
    print(42)
a()

import numpy as np
zeros = np.zeros(100)
print(zeros)

print([i for i in range(1000)])
\q'''
    s.sendall(code)
    data = s.recv(1024)
    out = data.decode()

print('Output:')
print(out)

