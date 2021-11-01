FROM python:3.7
COPY requirements/requirements.txt requirements/requirements.txt
RUN pip install -r requirements/requirements.txt
COPY /rumi/ /rumi
# we will just run our script.py as our docker entrypoint by python script.py
CMD ["python", "rumi/reporter.py --repo_path='../rotational.io/' --pattern='folder/"]