web: gunicorn loandesk.wsgi --log-file -
release: ./scripts/build_tailwind.sh && python manage.py migrate --noinput && python manage.py collectstatic --noinput
