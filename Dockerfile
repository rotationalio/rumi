FROM python:3.7
COPY requirements/requirements.txt requirements/requirements.txt
RUN pip install -r requirements/requirements.txt
COPY . .
CMD ["python", "rumi/rumi-hugo/action.py"]