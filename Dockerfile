FROM python:3.10-slim

ENV HOME=/home/app/event_abozar
RUN mkdir -p $HOME 

ENV PYTHONUNBUFFERED=1


# Set working directory
WORKDIR $HOME
COPY . $HOME

# Installing requirements
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

# Collect static files

CMD python manage.py migrate --no-input && \
    python manage.py collectstatic --no-input && \
    gunicorn -b 0.0.0.0:8080 config.wsgi:application --workers 3 --timeout 120