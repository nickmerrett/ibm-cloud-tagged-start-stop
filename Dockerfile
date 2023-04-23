FROM python:3.9-alpine

RUN pip install \
    --upgrade pip \
    ibm-vpc \
    ibm-platform-services 

COPY actionVSI.py /app/actionVSI.py
WORKDIR /app
CMD python /app/actionVSI.py
