


from celery import shared_task
from datetime import date, timedelta
from .models import Bill, Patients, User
import logging

@shared_task
def birthday_reminder():
    
    today = date.today()
    for i in range(1, 6):
        
        upcoming_date = today + timedelta(days=i)
        
        patients = Patients.objects.filter(
            date_of_birth__month=upcoming_date.month,
            date_of_birth__day=upcoming_date.day,
        )
        
        for patient in patients:
            print(f"🎂 Happy Birthday {patient.name}! Your birthday is on {upcoming_date.strftime('%d %B %Y')}")   
            

