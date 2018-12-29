# Install dependencies
FROM python:2.7-alpine as base
FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install" -r /requirements.txt

# Copy and run
FROM base
COPY --from=builder /install /usr/local
ADD . /app
WORKDIR /app
EXPOSE 5000
ENTRYPOINT ["python", "app.py"]
