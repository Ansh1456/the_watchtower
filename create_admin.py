import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'the_watchtower.settings')
django.setup()

from django.contrib.auth.models import User

admin_user = os.environ.get('ADMIN_USER')
admin_email = os.environ.get('ADMIN_EMAIL')
admin_pass = os.environ.get('ADMIN_PASS')

if admin_user and admin_pass:
    if not User.objects.filter(username=admin_user).exists():
        print(f"[*] Creating superuser '{admin_user}'...")
        User.objects.create_superuser(username=admin_user, email=admin_email, password=admin_pass)
        print("[+] Superuser created successfully!")
    else:
        print(f"[*] Superuser '{admin_user}' already exists. Skipping creation.")
else:
    print("[*] ADMIN_USER or ADMIN_PASS not set in environment. Skipping superuser creation.")
