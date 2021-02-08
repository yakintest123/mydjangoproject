from django.shortcuts import render,redirect
from .models import Patient,Contact,Doctor,Appointment,Transaction,CancelAppointment
from django.core.mail import send_mail
import random
from django.conf import settings
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def initiate_payment(request):
    try:
        amount = int(request.POST['appointment_fees'])
        patient = Patient.objects.get(email=request.session['email'])
        appointment=Appointment.objects.get(id=request.POST['appointment_id'])
        appointment.payment_status="completed"
        appointment.save()
    except:
        return render(request, 'appointment_fees_payment.html', context={'error': 'Wrong Account Details or amount'})

    transaction = Transaction.objects.create(made_by=patient, amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return redirect('index')
    else:
        return redirect('index')



def index(request):
    return render(request,'index.html')

def doctor_index(request):
    return render(request,'doctor_index.html')

def login(request):
    if request.method=="POST":
        usertype=request.POST['usertype']
        if usertype=="patient":
            try:
                patient=Patient.objects.get(
                    email=request.POST['email'],
                    password=request.POST['password'],
                )
                request.session['fname']=patient.fname
                request.session['lname']=patient.lname
                request.session['email']=patient.email
                return render(request, 'index.html')
            except:
                msg="Email or Password Is Incorrect"
                return render(request,'login.html',{'msg':msg})
        elif usertype=="doctor":
            try:
                doctor=Doctor.objects.get(
                    email=request.POST['email'],
                    password=request.POST['password'],
                )
                request.session['fname']=doctor.fname
                request.session['lname']=doctor.lname
                request.session['email']=doctor.email
                appointments=Appointment.objects.filter(doctor=doctor,status="pending")
                request.session['appointments_count']=len(appointments)
                return render(request, 'doctor_index.html')
            except:
                msg="Email or Password Is Incorrect"
                return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'login.html')

def signup(request):
    if request.method=="POST":
        try:
            patient=Patient.objects.get(email=request.POST['email'])
            if patient:
                msg="Email is already registered"
                return render(request,'signup.html',{'msg':msg})
        except:
            if not request.POST['password']==request.POST['cpassword']:
                msg="Password and Confirm Password does not match"
                return render(request,'signup.html',{'msg':msg})
            else:
                Patient.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    password=request.POST['password'],
                    cpassword=request.POST['cpassword'],
                )
                msg="Patient SignUp Sucessfully"
                return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'signup.html')

def about(request):
    doctors=Doctor.objects.all()
    return render(request,'about.html',{'doctors':doctors})

def services(request):
    return render(request,'services.html')

def contact(request):
    if request.method=="POST":
        Contact.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            mobile=request.POST['mobile'],
            remarks=request.POST['remarks'],
        )
        contacts=Contact.objects.all().order_by('-id')
        msg="Contact Saved Successfully"
        return render(request,'contact.html',{'msg':msg,'contacts':contacts})
    else:
        contacts=Contact.objects.all().order_by('-id')
        return render(request,'contact.html',{'contacts':contacts})

def team(request):
    return render(request,'team.html')

def logout(request):
    try:
        del request.session['fname']
        del request.session['lname']
        del request.session['email']
        return redirect('login')
    except:
        return redirect('login')

def forgot_password(request):
    if request.method=="POST":
        try:
            user=Patient.objects.get(email=request.POST['email'])
            rec=[request.POST['email'],]
            subject="OTP for Forgot Password"
            otp=random.randint(1000,9999)
            message="Your OTP for Forgot Password Is: "+str(otp)
            email_from = settings.EMAIL_HOST_USER
            send_mail(subject,message,email_from,rec)
            return render(request,'otp.html',{'otp':otp,'email':request.POST['email']})
        except:
            try:
                user=Doctor.objects.get(email=request.POST['email'])
                rec=[request.POST['email'],]
                subject="OTP for Forgot Password"
                otp=random.randint(1000,9999)
                message="Your OTP for Forgot Password Is: "+str(otp)
                email_from = settings.EMAIL_HOST_USER
                send_mail(subject,message,email_from,rec)
                return render(request,'otp.html',{'otp':otp,'email':request.POST['email']})
            except:
                msg="Email Does Not Exist"
                return render(request,'forgot_password.html',{'msg':msg})
    else:
        return render(request,'forgot_password.html')

def verify_otp(request):
    try:
        user=Patient.objects.get(email=request.POST['email'])
        if request.POST['otp']==request.POST['uotp']:
            return render(request,'new_password.html',{'email':request.POST['email']})
        else:
            msg="OTP Is Incorrect"
            return render(request,'otp.html',{'otp':request.POST['otp'],'email':request.POST['email'],'msg':msg})
    except:
        try:
            user=Doctor.objects.get(email=request.POST['email'])
            if request.POST['otp']==request.POST['uotp']:
                return render(request,'new_password.html',{'email':request.POST['email']})
            else:
                msg="OTP Is Incorrect"
                return render(request,'otp.html',{'otp':request.POST['otp'],'email':request.POST['email'],'msg':msg})
        except:
            return render(request,'otp.html',{'otp':request.POST['otp'],'email':request.POST['email'],'msg':msg})

def update_password(request):
    try:
        user=Patient.objects.get(email=request.POST['email'])
        if request.POST['password']==request.POST['cpassword']:
            user.password=request.POST['password']
            user.cpassword=request.POST['cpassword']
            user.save()
            return redirect('login')
        else:
            msg="Password and Confirm Password Does not Match"
            return render(request,'new_password.html',{'email':request.POST['email']})
    except:
        try:
            user=Doctor.objects.get(email=request.POST['email'])
            if request.POST['password']==request.POST['cpassword']:
                user.password=request.POST['password']
                user.cpassword=request.POST['cpassword']
                user.save()
                return redirect('login')
            else:
                msg="Password and Confirm Password Does not Match"
                return render(request,'new_password.html',{'email':request.POST['email']})
        except:
            pass

def change_password(request):
    if request.method=="POST":
        user=Doctor.objects.get(email=request.session['email'])
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                user.password=request.POST['new_password']
                user.cpassword=request.POST['new_password']
                user.save()
                return redirect('logout')
            else:
                msg="New Password and Confirm New Password Does Not Match"
                return render(request,'change_password.html',{'msg':msg})
        else:
            msg="Old Password Is Incorrect"
            return render(request,'change_password.html',{'msg':msg})

    else:
        return render(request,'change_password.html')

def doctor_profile(request):
    if request.method=="POST":
        doctor=Doctor.objects.get(email=request.session['email'])
        doctor.specialist=request.POST['specialist']
        doctor.address=request.POST['address']
        doctor.degree=request.POST['degree']
        doctor.consulting_charge=request.POST['consulting_charge']
        doctor.time_slot=request.POST['time_slot']
        try:
            doctor.doctor_image=request.FILES['doctor_image']
        except:
            pass
        doctor.save()
        return redirect('doctor_index')
    else:
        doctor=Doctor.objects.get(email=request.session['email'])
        return render(request,'doctor_profile.html', {'doctor':doctor})

def doctor_detail(request,pk):
    doctor=Doctor.objects.get(pk=pk)
    return render(request,'doctor_detail.html',{'doctor':doctor})

def book_appointment(request,pk):
    button=""
    patient=Patient.objects.get(email=request.session['email'])
    doctor=Doctor.objects.get(pk=pk)
    if request.method=="POST":
        try:
            button=request.POST['ba']
            appointment=Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                appointment_date=request.POST['appointment_date'],
                appointment_time=request.POST['appointment_time'],
                symptoms=request.POST['symptoms'],
            )
            print(appointment)
            return render(request,'appointment_fees_payment.html',{'appointment':appointment})
        except:
            appointments=Appointment.objects.filter(doctor=doctor,status="pending",appointment_date=request.POST['appointment_date'])
            l1=[]
            l2=['9:00 To 10:00','10:00 To 11:00','11:00 To 12:00']
            l3=[]
            for i in appointments:
                l1.append(i.appointment_time)
            for i in l2:
                if i not in l1:
                    l3.append(i)
            print(l3)
            return render(request,'book_appointment.html',{'patient':patient,'doctor':doctor,'appointment_date':request.POST['appointment_date'],'l3':l3})
    else:
        return render(request,'book_appointment.html',{'patient':patient,'doctor':doctor})

def view_appointment(request):
    doctor=Doctor.objects.get(email=request.session['email'])
    appointments=Appointment.objects.filter(doctor=doctor,status="pending")
    request.session['appointments_count']=len(appointments)
    return render(request,'view_appointment.html',{'appointments':appointments})

def complete_appointment(request,pk):
    appointment=Appointment.objects.get(pk=pk)
    appointment.status="completed"
    appointment.save()
    return redirect('view_appointment')

def my_appointments(request):
    patient=Patient.objects.get(email=request.session['email'])
    appointments=Appointment.objects.filter(patient=patient)
    print(appointments)
    for i in appointments:
        try:
            cancel_appointment=CancelAppointment.objects.get(appointment=i)
            if cancel_appointment:
                i.reason_for_cancel=cancel_appointment.reason_for_cancel
                i.save()
        except:
            pass
    appointments=Appointment.objects.filter(patient=patient)
    return render(request,'my_appointments.html',{'appointments':appointments})

def cancel_appointment(request,pk):
    if request.method=="POST":
        appointment=Appointment.objects.get(pk=pk)
        reason_for_cancel=request.POST['reason_for_cancel']
        appointment.status="cancelled"
        appointment.save()
        CancelAppointment.objects.create(appointment=appointment,reason_for_cancel=reason_for_cancel)
        return redirect('view_appointment')
    else:
        appointment=Appointment.objects.get(pk=pk)
        return render(request,'doctor_cancel_appointment.html',{'appointment':appointment})