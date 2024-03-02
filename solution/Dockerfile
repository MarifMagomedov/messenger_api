FROM python:3.12.1-alpine3.19

WORKDIR /test-python-MarifMagomedov

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV SERVER_PORT=8080

CMD ["sh", "-c", "exec python -m uvicorn app:app --host 0.0.0.0 --port $SERVER_PORT"]