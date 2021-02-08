from django.db import models
from django.utils import timezone

# Create your models here.

class Patient(models.Model):
    fname=models.CharField(max_length=200)
    lname=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    mobile=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    cpassword=models.CharField(max_length=200)
    patient_history=models.CharField(max_length=100,default="None")

    def __str__(self):
        return self.fname+" "+self.lname

class Doctor(models.Model):
    fname=models.CharField(max_length=200)
    lname=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    mobile=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    cpassword=models.CharField(max_length=200)
    specialist=models.CharField(max_length=100,default="")
    address=models.TextField(max_length=100,default="")
    degree=models.CharField(max_length=100,default="")
    consulting_charge=models.CharField(max_length=100,default="")
    time_slot=models.CharField(max_length=100,default="")
    doctor_image=models.ImageField(upload_to='images/',default="")

    def __str__(self):
        return self.fname+" "+self.lname

class Contact(models.Model):
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    mobile=models.CharField(max_length=200)
    remarks=models.TextField()

    def __str__(self):
        return self.name

class Appointment(models.Model):
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE)
    patient=models.ForeignKey(Patient,on_delete=models.CASCADE)
    appointment_date=models.CharField(max_length=100)
    appointment_time=models.CharField(max_length=100)
    symptoms=models.TextField()
    status=models.CharField(max_length=100,default="pending")
    payment_status=models.CharField(max_length=100,default="pending")
    reason_for_cancel=models.TextField(default="")

    def __str__(self):
        return self.patient.fname+" - "+self.doctor.fname

class Transaction(models.Model):
    made_by = models.ForeignKey(Patient, related_name='transactions', 
                                on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)

class CancelAppointment(models.Model):
    appointment=models.ForeignKey(Appointment,on_delete=models.CASCADE)
    reason_for_cancel=models.TextField()

    def __str__(self):
        return self.appointment.patient.fname+" - "+self.appointment.doctor.fname