# Socket server for executing arbitrary python code
Creates a worker for each CPU core on the host computer. Each worker creates a socket server that uses a local unix socket located at `/tmp/.py-runner/py_runnerN.sock` where N is the worker number (starting at 0). Each socket server reads in 128 bytes which contains the message size of the incoming python code, reads in the message containing python code using this message length, executes the python code, and returns the STDOUT to the connected client. Server is run in a docker container which shares the `/tmp/.py-runner` folder with the host OS so the host OS can communicate with the server.

# Setup

Make sure you have python 3.8 installed and are using it for the following commands

Install requirements
`$ pip install -r requirements.txt`

Install pre-commit hook
`$ pre-commit install --hook-type pre-push`


# Running

Use docker build and run scripts to build and run using docker, to run using just python:
`$ python py-runner.py`

Test using test script:
`$ python test_send.py`

