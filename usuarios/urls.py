# Em Biblioteca/usuarios/urls.py
from django.urls import path

from .views import ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView

app_name = 'usuarios'

urlpatterns=[
  
  path('gerenciar/', ClienteListView.as_view(), name='lista_clientes'),
  path('cadastro/', ClienteCreateView.as_view(), name='cadastro_cliente'),
  path('editar/<int:pk>/', ClienteUpdateView.as_view(), name='editar_cliente'),
  path('excluir/<int:pk>/', ClienteDeleteView.as_view(), name='excluir_cliente'),
]

