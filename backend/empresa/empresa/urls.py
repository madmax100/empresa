
from django.contrib import admin
from django.urls import path, include
import contas.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include(contas.urls)),
    path('api/', include(contas.urls)),
]
