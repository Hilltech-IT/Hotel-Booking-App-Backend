FROM python:3-slim
WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

ENV BACKEND_URL=http://34.171.61.167:8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]