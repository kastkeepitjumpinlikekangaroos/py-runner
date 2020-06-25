import socket
import os

for _ in range(100):
    for i in range(os.cpu_count()):

        socket_loc = f'/tmp/py_runner{i}.sock'

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(socket_loc)
            code = b'''
import numpy as np
import random

random_vec = np.random.rand(3)
random_vec_2 = np.random.rand(3)

random_coefficient = random.randint(-10, 10)
random_coefficient_2 = random.randint(-10, 10)

question = f"What is {random_coefficient} * {random_vec.tolist()} + {random_coefficient_2} * {random_vec_2.tolist()}?"
answer = (random_coefficient * random_vec) + (random_coefficient_2 * random_vec_2)

print(question)
print(answer.tolist())

        '''
            message_len = len(code)
            header = str(message_len)
            header = header + '-' * (128 - len(header))  # pad first 128 bytes
            s.sendall(header.encode() + code)
            
            message_len_raw = s.recv(128)
            message_len_decoded = message_len_raw.decode()
            message_len = int(message_len_decoded.replace('-', '')) 
            message = s.recv(message_len)
            output = message.decode()

        print('Output:')
        print(output)

