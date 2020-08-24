FROM python:3.8.2-slim-buster
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY DockerImageMiner.py /
CMD ["python3","-u","DockerImageMiner.py"]