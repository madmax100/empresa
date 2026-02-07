from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/core/", include("apps.core.urls")),
    path("api/estoque/", include("apps.estoque.urls")),
    path("api/contas/", include("apps.contas.urls")),
    path("api/faturamento/", include("apps.faturamento.urls")),
    path("api/contratos_locacao/", include("apps.locacao.urls")),
]
