import os
import traceback
import subprocess
import rx
from rx import operators as ops
from rx.scheduler import ThreadPoolScheduler
import tempfile
import socket

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
                print(f'Handling requests on {socket_loc}')
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

socket_locs = [f'/tmp/py_runner{i}.sock' for i in range(os.cpu_count())]

executor = ThreadPoolScheduler()
for socket_loc in socket_locs:
    rx.from_(get_input(socket_loc)).pipe(
        ops.map(lambda x: x),
        ops.subscribe_on(executor),
    ).subscribe(get_output, lambda e: print(e), lambda: print('Finished execution'))

end = ''
while end != 'q':
    end = input('Enter q to quit: ')
    print()

