# Socket server for executing arbitrary python code
Creates a unix socket located at `/tmp/py_runner.sock`. When reading a message the server reads in 128 bytes which contains the message size of the incoming python code padded with '-' until we reach 128 bytes. The server then uses this message length to read in a message containing python code. The server then executes the python code and returns the STDOUT to the connected client (sends the size of the message and then the message just like before). If the environment variable `SECURE` is set to anything the python code will be executed in a docker (or podman if `PODMAN` environment variable is set) container, otherwise all code will be executed on the native `python3` installation.

# Running

Build container (if using secure mode):

`$ ./build_cont.sh docker`
or
`$ ./build_cont.sh podman`

Run server:

`$ python3 py_runner.py`


# Testing

First start server and then run tests with

`$ python3 -m unittest test_py_runner.py`
