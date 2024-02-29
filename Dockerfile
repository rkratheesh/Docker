FROM python:latest

WORKDIR /Horilla

COPY requirements.txt  requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

CMD python manage.py runserver
