from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("login/", views.login_view, name="login"),
    path("user/", views.user_dashboard, name="user_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("system-info/", views.system_info_page, name="system_info"),
    path("api/system-data/", views.system_data_api, name="system_data_api"),
    path("api/network-speed/", views.network_speed_api, name="network_speed_api"),
    path("api/map-data/", views.map_data_api, name="map_data_api"),
    path("logout/", views.logout_view, name="logout"),
    path("monitoring/", views.monitoring_page, name="monitoring"),
    path("system-details/", views.system_details, name="system_details"),
    path("register/", views.register_view, name="register"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("manage-users/", views.admin_users, name="admin_users"),
    path("delete-user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("user-system/<int:user_id>/", views.view_user_system, name="view_user_system"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("export-telemetry/", views.export_telemetry, name="export_telemetry"),
    path("api/update-location/", views.update_location_api, name="update_location_api"),
    path("api/telemetry/push/", views.PushTelemetryView.as_view(), name="push_telemetry"),
]
