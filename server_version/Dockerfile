FROM python:3.9-slim

RUN pip install flask urllib3

COPY . /app

EXPOSE 5000

WORKDIR /app

CMD ["flask", "--app", "server", "run", "--host=0.0.0.0"]