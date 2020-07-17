import asyncio
import logging
import traceback
import subprocess
import tempfile
import os
from functools import partial
from concurrent.futures import ThreadPoolExecutor

SOCKET_LOC = '/tmp/py_runner.sock'
HEADER_LEN = 128


async def main(loop):
    logging.info('Serving on {SOCKET_LOC}'.format(SOCKET_LOC=SOCKET_LOC))
    executor = ThreadPoolExecutor(max_workers=os.cpu_count())
    __handle_connection = partial(_handle_connection, executor=executor, loop=loop)
    server = await asyncio.start_unix_server(__handle_connection, SOCKET_LOC)

    async with server:
        await server.serve_forever()


async def _handle_connection(reader, writer, loop, executor):
    addr = writer.get_extra_info('peername')
    logging.info('Handling request for {addr} on {SOCKET_LOC}'
                 .format(addr=addr, SOCKET_LOC=SOCKET_LOC))

    message_len_raw = await reader.read(HEADER_LEN)
    message_len_decoded = message_len_raw.decode()
    message_len = int(message_len_decoded.replace('-', ''))

    message = await reader.read(message_len)
    code = message.decode()
    logging.info('Running:\n\n{code}'.format(code=code))

    output = await loop.run_in_executor(executor, _exec_code, code)

    message_len = len(output)
    header = str(message_len)
    # encode message length in first HEADER_LEN bytes
    header = header + '-' * (HEADER_LEN - len(header))
    writer.write(header.encode() + output)
    await writer.drain()
    logging.info('Close the connection for {addr}'.format(addr=addr))
    writer.close()


def _exec_code(code: str) -> bytes:
    with tempfile.NamedTemporaryFile() as f:
        f.write(code.encode())
        f.seek(0)
        try:
            cmd = 'docker run py_exec -v {f_name}:/tmp/run.py'.format(f_name=f.name),
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = _log_error(e).encode()
    _log_output(output)
    return output


def _log_output(output: bytes) -> str:
    decoded_out = output.decode()
    logging.info(decoded_out)
    return decoded_out


def _log_error(e) -> str:
    err = traceback.format_exc()
    err = 'Error: {e}\n\n{err}'.format(e=e, err=err)
    logging.warning(err)
    return err


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
