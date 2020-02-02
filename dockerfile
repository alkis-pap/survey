FROM python:3

RUN mkdir -p /usr/src/survey
COPY . /usr/src/survey
WORKDIR /usr/src/survey
RUN pip install -r requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:5898", "--reload", "-c", "config.py", "app:app"]