FROM python:3.14

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install --with-deps

RUN apt-get update && apt-get install -y \
    libxml2-dev \
	libxslt1-dev \
	zlib1g-dev \
	gcc \
	&& rm -rf /var/lib/apt/lists/*
	
RUN pip install lxml

COPY remoteok_api/ ./remoteok_api/

EXPOSE 8000

CMD ["uvicorn", "remoteok_api.main:app", "--host", "0.0.0.0", "--port", "8000"]