FROM python:3.8

RUN mkdir -p /py-runner

WORKDIR /py-runner

COPY ./ ./

RUN pip install -r requirements.txt

CMD ["sh", "-c", "python to_run.py"]

