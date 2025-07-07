FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# اجرای دستورات به صورت مستقیم (بدون فایل sh)
CMD ["sh", "-c", "\
  echo 'prozhe dare run mishe sabr kon' && \
  python manage.py migrate && \
  echo 'prozhe run shod' && \
  echo 'mitoni swagger ro toye in urls bebini:' && \
  echo 'http://localhost:8000' && \
  python manage.py runserver 0.0.0.0:8000"]