import os
import subprocess
import tempfile
import socket
import logging

HEADER_LEN = 128 



def listen_on_unix_socket(socket_loc: str) -> bytes:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        if os.path.exists(socket_loc):
            os.remove(socket_loc)
        s.bind(socket_loc)
        s.listen()
        logging.info(f'Listening to socket located at {socket_loc}')
        while True:
            conn, addr = s.accept()
            with conn:
                logging.info(f'Handling request on {socket_loc}')
                message_len_raw = conn.recv(HEADER_LEN)
                message_len_decoded = message_len_raw.decode()
                message_len = int(message_len_decoded.replace('-', ''))

                message = conn.recv(message_len)
                code = message.decode()
                logging.info(f'Running:\n\n{code}')

                with tempfile.NamedTemporaryFile() as f:
                    f.write(code.encode())
                    f.seek(0)
                    try:
                        output = subprocess.check_output(f'python {f.name}', shell=True, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as e:
                        output = traceback.format_exc().encode()
                        output = f'Error: {e}\n\n{output}'
                        logging.warning(output)
                    message_len = len(output)
                    header = str(message_len)
                    header = header + '-' * (HEADER_LEN - len(header))  # encode message length in first HEADER_LEN bytes
                    conn.sendall(header.encode() + output)
                    yield output


