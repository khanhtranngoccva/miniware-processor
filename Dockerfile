FROM python:3.10
LABEL authors="Khanh"

WORKDIR /setup
COPY requirements.txt /setup
RUN pip install -r requirements.txt
RUN pip install -U py-mon

WORKDIR /application
COPY install_tools.sh .
RUN bash ./install_tools.sh

COPY ./ /application
ENTRYPOINT ["pymon", "main.py"]