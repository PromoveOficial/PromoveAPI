FROM python:latest

WORKDIR /promove_api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# RUN useradd -m apiuser
# RUN chmod -R 777 /promove_api
# # RUN chown -R apiuser:apiuser /promove_api/


# # USER apiuser

COPY . .

EXPOSE 8000

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "app:app" ]