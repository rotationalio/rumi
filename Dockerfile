FROM python:3.7
COPY requirements/requirements.txt requirements/requirements.txt
RUN pip install -r requirements/requirements.txt
COPY /rumi/ /rumi
CMD ["git clone https://github.com/rotationalio/rotational.io.git"]
CMD ["python", "rumi/action.py"]