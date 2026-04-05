from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include("catalog.urls")),
    path('sales/', include("sales.urls")),
]

handler403 = 'catalog.views.error_403'