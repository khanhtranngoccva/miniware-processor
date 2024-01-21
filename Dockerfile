FROM python:3.10
LABEL authors="Khanh"

WORKDIR /setup
COPY requirements.txt /setup
RUN pip install -r requirements.txt

WORKDIR /application
COPY install_tools.sh .
RUN bash ./install_tools.sh

COPY ./ /application
ENTRYPOINT ["python", "main.py"]