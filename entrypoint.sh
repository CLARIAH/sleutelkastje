flask --app sleutelkastje db upgrade

gunicorn -b :5000 -t 60 -w 1 --threads 4 sleuelkastje:app
