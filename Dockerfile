FROM python:3.12-slim
WORKDIR /app
COPY pos_api.py .
COPY catalog.db .
RUN pip install flask
EXPOSE 5000
CMD ["python", "pos_api.py"]   
