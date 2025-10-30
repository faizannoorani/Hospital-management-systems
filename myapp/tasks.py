
from celery import shared_task
from .models import Bill
from .models import Patients

@shared_task
def check_pending_amounts():
    bills = Bill.objects.filter(amount_status='pending')
    for p in bills:
        patient_name=p.appointment.patient.name
        print(f"reminder: {patient_name} appointment amount is pending")
    return "Checked all Pending users"
