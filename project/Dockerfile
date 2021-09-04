FROM python:3.9.0

LABEL maintainer="Bharath Kumar"

COPY techtrends/ /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN python3 init_db.py

EXPOSE 3111

CMD [ "python3", "app.py" ]

