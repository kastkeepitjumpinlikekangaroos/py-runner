FROM python:3.8

RUN mkdir -p /py_exec

WORKDIR /py_exec

CMD ["sh", "-c", "python /py_exec/run.py"]
