import os
import logging
import traceback

import rx
from rx import operators as ops
from rx.scheduler import ThreadPoolScheduler

from lib.server import listen_on_unix_socket

SOCKETS_DIR = '/tmp/.py-runner'


def main():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    if not os.path.exists(SOCKETS_DIR):
        os.mkdir(SOCKETS_DIR)

    socket_locs = [f'{SOCKETS_DIR}/py_runner{i}.sock' for i in range(os.cpu_count())]

    scheduler = ThreadPoolScheduler()
    for socket_loc in socket_locs:
        _spawn_worker(scheduler, socket_loc)


def _spawn_worker(scheduler: ThreadPoolScheduler, socket_loc: str):
    rx.from_(listen_on_unix_socket(socket_loc)).pipe(
        ops.map(lambda x: x),
        ops.subscribe_on(scheduler),
    ).subscribe(
        _log_output,
        _log_error,
        lambda: logging.info(f'Finished execution on {socket_loc}')
    )


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
    main()
