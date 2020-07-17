import multiprocessing
import socket
import unittest


SOCKET_LOC = '/tmp/py_runner.sock'


class TestStringMethods(unittest.TestCase):
    def test_send(self):
        with multiprocessing.Pool() as p:
            iter_ = [i for i in range(40)]
            results = p.map(_run_test, iter_)
            for res in results:
                self.assertTrue('What is' in res)


def _run_test(j):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(SOCKET_LOC)
        code = b'''
import random
random_coefficient = random.randint(0, 20)
random_coefficient_2 = random.randint(-10, 89)
question = f"What is {random_coefficient} * {random_coefficient_2}?"
answer = random_coefficient * random_coefficient_2

print(question)
print(answer)

    '''
        message_len = len(code)
        header = str(message_len)
        header = header + '-' * (128 - len(header))
        s.sendall(header.encode() + code)

        message_len_raw = s.recv(128)
        message_len_decoded = message_len_raw.decode()
        message_len = int(message_len_decoded.replace('-', ''))
        message = s.recv(message_len)
        output = message.decode()
        return output


if __name__ == '__main__':
    unittest.main()
