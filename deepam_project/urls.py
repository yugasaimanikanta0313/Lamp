from django.contrib import admin
from django.urls import include, path


urlpatterns = [
	path("admin/", admin.site.urls),
	path("", include("deepam.urls")),
	path("accounts/", include("accounts.urls")),
]
