FROM python:3.7
COPY requirements/requirements.txt requirements/requirements.txt
RUN pip install -r requirements/requirements.txt
COPY /rumi/ /rumi
COPY ../rotational.io/ ../rotational.io/
CMD ["python", "rumi/action.py"]