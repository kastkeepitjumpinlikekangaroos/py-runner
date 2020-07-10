import asyncio
import logging
import traceback
import subprocess
import tempfile

SOCKET_LOC = '/tmp/.py-runner/py_runner.sock'
HEADER_LEN = 128


async def handle_connection(reader, writer):
    addr = writer.get_extra_info('peername')
    logging.info(f'Handling request for {addr} on {SOCKET_LOC}')
    message_len_raw = await reader.read(HEADER_LEN)
    message_len_decoded = message_len_raw.decode()
    message_len = int(message_len_decoded.replace('-', ''))

    message = await reader.read(message_len)
    code = message.decode()
    logging.info(f'Running:\n\n{code}')

    with tempfile.NamedTemporaryFile() as f:
        f.write(code.encode())
        f.seek(0)
        try:
            output = subprocess.check_output(f'python {f.name}', shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = _log_error(e).encode()
    _log_output(output)
    message_len = len(output)
    header = str(message_len)
    # encode message length in first HEADER_LEN bytes
    header = header + '-' * (HEADER_LEN - len(header))
    writer.write(header.encode() + output)
    await writer.drain()
    logging.info("Close the connection for {addr}")
    writer.close()


async def main():
    logging.info(f'Serving on {SOCKET_LOC}')
    server = await asyncio.start_unix_server(
        handle_connection, SOCKET_LOC)

    async with server:
        await server.serve_forever()


def _log_output(output):
    decoded_out = output.decode()
    logging.info(decoded_out)
    return decoded_out


def _log_error(e):
    err = traceback.format_exc()
    err = f'Error: {e}\n\n{err}'
    logging.warning(err)
    return err


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    asyncio.run(main())
