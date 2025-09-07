from django.urls import path
from . import views
 
urlpatterns = [
    path("grafico/", views.ocorrencias, name="grafico"),
    path('dashboard/grafico/', views.ocorrencias, name='dashboard'),
]
