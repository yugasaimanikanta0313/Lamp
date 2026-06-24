from django.urls import path

from .views import dashboard, lamp_detail


urlpatterns = [
	path("", dashboard, name="dashboard"),
    path("lamp/<int:lamp_id>/", lamp_detail, name="lamp_detail"),
]
