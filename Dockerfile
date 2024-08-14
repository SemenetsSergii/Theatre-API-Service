FROM python:3.11.6-alpine3.18
LABEL maintainer="serheysemenets@gmail.com"

ENV PYTHOUNNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "manage.py", "runserver" ,"0.0.0.0:8000"]

RUN mkdir -p /app/media && \
    adduser --disabled-password --no-create-home my_user && \
    chown -R my_user /app && \
    chmod -R 755 /app/media

USER my_user
