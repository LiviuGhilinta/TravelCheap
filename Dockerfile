FROM python:3.13.5


WORKDIR /TravelCheap

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt


COPY . .

WORKDIR /TravelCheap/src
CMD [ "python3", "Airport_Search.py" ]