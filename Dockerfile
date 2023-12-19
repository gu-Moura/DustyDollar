FROM python:3.11.7-slim-bookworm

LABEL authors="gmoura"

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /code

WORKDIR /code/src

CMD ["python3", "start-server.py"]