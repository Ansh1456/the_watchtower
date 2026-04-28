from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .services.system_service import get_system_info, get_user_system_info
from .services.auth_service import generate_and_send_otp
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import User
import psutil
import time






# LANDING PAGE (3D Cinematic)
def landing_page(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("admin_dashboard")
        return redirect("user_dashboard")
    return render(request, "landing.html")

# LOGIN PAGE
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("admin_dashboard")
            else:
                return redirect("user_dashboard")

    return render(request, "login.html")



# USER DASHBOARD
@login_required
def user_dashboard(request):
    system_data = get_user_system_info(request.user)
    return render(request, "dashboard_user.html", {"data": system_data})




# ADMIN DASHBOARD
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("user_dashboard")

    system_data = get_user_system_info(request.user)

    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = User.objects.filter(is_staff=True).count()

    uptime_seconds = time.time() - psutil.boot_time()
    uptime_hours = int(uptime_seconds // 3600)

    context = {
        "data": system_data,
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "system_uptime": uptime_hours
    }

    return render(request, "dashboard_admin.html", context)


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def system_info_page(request):
    system_data = get_user_system_info(request.user)
    return render(request, "system_info.html", {"data": system_data})

@login_required
def system_data_api(request):
    # Transitioning to Remote Agent Architecture (v3.0)
    # Pull accurate live telemetry from the authenticated user's remote agent
    
    from accounts.models import UserProfile
    import psutil

    try:
        profile = request.user.userprofile
        cpu = profile.latest_cpu if profile.latest_cpu else 0.0
        ram = profile.latest_ram if profile.latest_ram else 0.0
        disk = profile.latest_disk if profile.latest_disk else 0.0
    except UserProfile.DoesNotExist:
        # Fallback to local if no profile
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

    return JsonResponse({
        "cpu": cpu,
        "ram": ram,
        "disk": disk
    })

@login_required
def network_speed_api(request):
    from .services.system_service import get_network_speed
    speed_data = get_network_speed()
    return JsonResponse(speed_data)

@login_required
def monitoring_page(request):
    return render(request, "monitoring.html")

@login_required
def system_details(request):
    data = get_user_system_info(request.user)
    return render(request,"system_details.html",{"data":data})


from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
def map_data_api(request):
    if not request.user.is_superuser:
        return JsonResponse({"error": "Unauthorized"}, status=403)
        
    users = User.objects.select_related('userprofile').all()
    data = []
    for u in users:
        try:
            profile = u.userprofile
            data.append({
                "id": u.id,
                "username": u.username,
                "is_admin": u.is_superuser,
                "is_active": u.is_active,
                "lat": profile.latitude,
                "lng": profile.longitude,
                "cpu": profile.latest_cpu,
                "ram": profile.latest_ram,
                "disk": profile.latest_disk,
            })
        except:
            pass
    return JsonResponse(data, safe=False)

def register_view(request):

    if request.method == "POST":

        fullname = request.POST.get("fullname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        otp = generate_and_send_otp(email)

        print("OTP:", otp)

        request.session["otp"] = otp
        request.session["email"] = email
        request.session["reg_data"] = {
            "fullname": fullname,
            "username": username,
            "email": email,
            "password": password
        }

        messages.info(request, "Verification code sent to your email. Check spam if not found.")
        return redirect("verify_otp")

    return render(request, "register.html")


def verify_otp(request):

    # prevent direct access
    if not request.session.get("otp") or not request.session.get("reg_data"):
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    if request.method == "POST":

        entered_otp = request.POST.get("otp")
        real_otp = request.session.get("otp")

        print("Entered:", entered_otp)
        print("Real:", real_otp)

        if str(entered_otp) == str(real_otp):

            data = request.session.get("reg_data")

            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"]
            )

            user.first_name = data["fullname"]
            user.save()

            request.session.pop("otp", None)
            request.session.pop("reg_data", None)
            request.session.pop("email", None)

            messages.success(request, "Account created successfully!")
            return redirect("login")

        else:
            messages.error(request, "Invalid verification code. Try again.")

    return render(request, "verify_otp.html")

from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

@staff_member_required
def admin_users(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "admin_users.html", {"users": users})
from django.shortcuts import redirect
from django.contrib.auth.models import User

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)

    # prevent admin deleting themselves
    if user != request.user:
        user.delete()

    return redirect("admin_users")

def view_user_system(request, user_id):
    if not request.user.is_superuser:
        return redirect("user_dashboard")

    user = User.objects.get(id=user_id)

    system_data = get_user_system_info(user)

    context = {
        "target_user": user,
        "data": system_data
    }

    return render(request, "system_details.html", context)

from django.shortcuts import redirect
from django.conf import settings


def resend_otp(request):

    email = request.session.get("email")
    
    # Fallback to getting email from reg_data if not in email key
    if not email:
        reg_data = request.session.get("reg_data")
        if reg_data:
            email = reg_data.get("email")

    if not email:
        messages.error(request, "No email found. Please register again.")
        return redirect("register")

    otp = generate_and_send_otp(email)
    request.session["otp"] = otp
    messages.success(request, "New code sent. Check your email.")

    return redirect("verify_otp")

from django.http import HttpResponse
import csv
from datetime import datetime


def export_telemetry(request):

    format_type = request.GET.get("format", "csv")

    # Only CSV for now
    if format_type != "csv":
        return HttpResponse("Only CSV supported for now")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="telemetry.csv"'

    writer = csv.writer(response)

    # Header
    writer.writerow(["Timestamp", "CPU Usage (%)", "RAM Usage (%)"])

    # Dummy data (you can later replace with real logs)
    for i in range(5):
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            20 + i,   # fake CPU
            40 + i    # fake RAM
        ])

    return response

import json

@login_required
def update_location_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            lat = float(data.get("lat"))
            lng = float(data.get("lng"))
            
            # Update user profile
            profile = request.user.userprofile
            profile.latitude = lat
            profile.longitude = lng
            profile.save()
            
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SystemLog, UserProfile
from django.utils import timezone

class PushTelemetryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cpu = request.data.get('cpu')
        ram = request.data.get('ram')
        disk = request.data.get('disk')
        disk_total = request.data.get('disk_total')
        disk_free = request.data.get('disk_free')
        
        # Static Hardware Info
        os_sys = request.data.get('os_sys')
        processor = request.data.get('processor')
        cores = request.data.get('cores')
        ram_total = request.data.get('ram_total')
        uptime = request.data.get('uptime')

        if cpu is None or ram is None or disk is None:
            return Response({"error": "Missing parameters"}, status=400)

        # Log it to SystemLog
        SystemLog.objects.create(
            user=request.user,
            cpu_usage=float(cpu),
            ram_usage=float(ram),
            disk_usage=float(disk)
        )

        # Update the UserProfile latest_ metrics for map and quick lookups
        profile = request.user.userprofile
        profile.latest_cpu = float(cpu)
        profile.latest_ram = float(ram)
        profile.latest_disk = float(disk)
        if disk_total is not None:
            profile.latest_disk_total = float(disk_total)
        if disk_free is not None:
            profile.latest_disk_free = float(disk_free)
            
        # Update static hardware info if provided
        if os_sys is not None:
            profile.os_sys = os_sys
        if processor is not None:
            profile.processor = processor
        if cores is not None:
            profile.cores = int(cores)
        if ram_total is not None:
            profile.ram_total = float(ram_total)
        if uptime is not None:
            profile.uptime_hours = float(uptime)
            
        profile.save()

        return Response({"status": "success", "timestamp": timezone.now()})