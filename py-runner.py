import os
import traceback
import subprocess
import concurrent.futures
import rx
from rx import operators as ops
import tempfile
import socket

# TODO: add some way to dynamically spawn new workers (with new socket server) so we can handle multiple connections at once

def get_input(socket_loc: str):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        if os.path.exists(socket_loc):
            os.remove(socket_loc)
        s.bind(socket_loc)
        s.listen()
        print(f'Listening to socket located at {socket_loc}')
        while True:
            conn, addr = s.accept()
            lines = []
            with conn:
                print('Connected by', addr)
                message_len_raw = conn.recv(128)
                message_len_decoded = message_len_raw.decode()
                message_len = int(message_len_decoded.replace('-', '')) 
                    
                message = conn.recv(message_len)
                code = message.decode()

                print('Running:')
                print(code)

                with tempfile.NamedTemporaryFile() as f:
                    f.write(code.encode())
                    f.seek(0)
                    try:
                        output = subprocess.check_output(f'python3 {f.name}', shell=True, stderr=subprocess.STDOUT)  
                    except subprocess.CalledProcessError as e:
                        output = traceback.format_exc().encode()
                        print(output)
                    message_len = len(output)
                    header = str(message_len)
                    header = header + '-' * (128 - len(header))  # pad first 128 bytes
                    conn.sendall(header.encode() + output)
                    yield output


def get_output(output):
    decoded_out = output.decode()
    print(decoded_out)
    return decoded_out 


def return_item(item):
    return item

socket_loc = '/tmp/py_runner.sock'

with concurrent.futures.ThreadPoolExecutor(5) as executor: 
    rx.from_(get_input(socket_loc)).pipe(
        ops.flat_map(lambda item: executor.submit(return_item, item)),
    ).subscribe(get_output)
    

print("Done executing")

