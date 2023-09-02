FROM python:3.10.12
RUN mkdir /weather_app
WORKDIR weather_app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chmod a+x start_docker/*.sh