FROM python:3.8-alpine

WORKDIR /app/babka

COPY . /app/babka

RUN pip3 install -r /app/babka/requirements.txt

CMD ["python3", "/app/babka/main.py"]
