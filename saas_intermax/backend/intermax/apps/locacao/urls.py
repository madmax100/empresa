from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.locacao import views

router = DefaultRouter()
router.register("", views.ContratoLocacaoViewSet, basename="contrato-locacao")

urlpatterns = [
    path("suprimentos/", views.SuprimentosPorContratoView.as_view(), name="suprimentos-por-contrato"),
    path("", include(router.urls)),
]
