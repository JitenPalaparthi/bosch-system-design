FROM python:3.12-slim
WORKDIR /app
COPY app.py /app/app.py
RUN pip install --no-cache-dir flask==3.0.3
EXPOSE 5002
CMD ["python", "app.py"]
