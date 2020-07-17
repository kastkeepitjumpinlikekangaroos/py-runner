# Socket server for executing arbitrary python code
Creates a unix socket located at `/tmp/py_runner.sock`. When reading a message the server reads in 128 bytes which contains the message size of the incoming python code padded with '-' until we reach 128 bytes. The server then uses this message length to read in a message containing python code. The server then executes the python code and returns the STDOUT to the connected client (sends the size of the message and then the message just like before). All python code is run in a docker container that is thrown away so any arbitrary code can be executed.

# Running

Use docker build script to create the docker container to run the python code, and then run `py_runner.py` with python 3.4+

Build docker:

`$ ./build_docker.sh`

Run server:

`$ python3 py_runner.py`


# Testing

First start server and then run tests with

`$ python3 -m unittest tests/test*`
