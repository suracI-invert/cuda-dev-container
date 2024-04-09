celery -A tasks worker &
uvicorn main:app --host=0.0.0.0