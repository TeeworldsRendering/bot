FROM python:3.8-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]

# docker build -t tw-renderer .
# docker run -it -v $PWD/public:/app/public tw-renderer