
from celery import shared_task
from .models import Bill
from .models import Patients
from .models import User 
import logging

from celery import shared_task
from .models import Bill

from celery import shared_task
from .models import Bill

@shared_task
def check_pending_amounts():
    bills = Bill.objects.filter(amount_status='PENDING').select_related(
        "appointment__patient"
    )

    for b in bills:
        print(f"Patient Name: {b.appointment.patient.name} amount is pending")

    print("Hello! Celery task is running 🚀")
    return "All pending bill users printed"
