from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('G_mindApp.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    
]