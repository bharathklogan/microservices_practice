FROM python:3.7-slim

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
EXPOSE 5000
# Install production dependencies.

RUN apt-get update && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

CMD [ "python", "app.py" ]