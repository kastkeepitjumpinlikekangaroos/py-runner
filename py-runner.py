import subprocess
import concurrent.futures
import rx
from rx import operators as ops
import tempfile
import socket

HOST = '127.0.0.1'
PORT = 65432

connections = []


def get_input():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'Listening on {(HOST, PORT)}')
        while True:
            conn, addr = s.accept()
            lines = []
            with conn:
                print('Connected by', addr)
                while True:
                    line = conn.recv(1024)
                    decoded_line = line.decode()
                    if decoded_line is not None and decoded_line != '\q':
                        lines.append(decoded_line)
                    else:
                        break

                    if '\q' in decoded_line:
                        break

                in_ = ''.join(lines).replace('\q', '') 
                print('Running:')
                print(in_)
                with tempfile.NamedTemporaryFile() as f:
                    f.write(in_.encode())
                    f.seek(0)
                    output = subprocess.check_output(f'python3 {f.name}', shell=True, stderr=subprocess.STDOUT)  
                    conn.sendall(output)
                    yield output


def get_output(output):
    decoded_out = output.decode()
    print(decoded_out)
    return decoded_out 


def return_item(item):
    return item


with concurrent.futures.ThreadPoolExecutor(5) as executor: 
    rx.from_(get_input()).pipe(
        ops.flat_map(lambda item: executor.submit(return_item, item)),
    ).subscribe(get_output)
    

print("Done executing")

