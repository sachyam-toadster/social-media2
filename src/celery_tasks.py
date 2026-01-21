from celery import Celery
from src.mail import mail, create_message
from asgiref.sync import async_to_sync

celery_tasks = Celery()

celery_tasks.config_from_object("src.config")

@celery_tasks.task()
def send_email(recipients: list[str], subject: str, body: str):

    message = create_message(recipients=recipients, subject=subject, body=body)

    async_to_sync(mail.send_message)(message)
    print("Email sent")