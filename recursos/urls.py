from django.urls import path
from .views import Inicio,Recurso,criar_reserva, detalhes_reserva, finalizar_reserva, remover_recurso, ReservaListView, MultaListView, EmprestimoListView,ReservaUpdateView, ReservaDeleteView,MultaUpdateView,MultaDeleteView,registrar_devolucao, registrar_dano, renovar_emprestimo,ExemplarCreateView,  ExemplarUpdateView,ExemplarListView,ExemplarDeleteView, RecursoGerenciarListView, RecursoCreateView, RecursoUpdateView, RecursoDeleteView, confirmar_emprestimo,reserva_futura

from django.contrib.auth import views as auth_view

app_name = 'recursos'

urlpatterns = [
	path('',Inicio.as_view(), name = 'inicio'),
  path('subtipo/<int:pk>/', Recurso.as_view(), name='lista_recursos'),
  path('criar-reserva/<int:pk>/', criar_reserva, name='criar_reserva'),
  path('reserva/', detalhes_reserva, name='detalhes_reserva'),
  path('login/', auth_view.LoginView.as_view(template_name='login.html'),name='login'),
  path('logout/', auth_view.LogoutView.as_view(),name = 'logout'),
  path('finalizar-reserva/', finalizar_reserva, name='finalizar_reserva'),
  path('remover-reserva/<int:pk>/', remover_recurso, name='remover_reserva'),
  path('gerenciar/reservas/', ReservaListView.as_view(), name='lista_reservas'),
  path('gerenciar/multas/', MultaListView.as_view(), name='lista_multas'),
  path('gerenciar/emprestimos/', EmprestimoListView.as_view(), name='lista_emprestimos'),
  path('gerenciar/reservas/editar/<int:pk>/', ReservaUpdateView.as_view(), name='editar_reserva'),
  path('gerenciar/reservas/cancelar/<int:pk>/', ReservaDeleteView.as_view(), name='cancelar_reserva'),
  path('gerenciar/multas/editar/<int:pk>/', MultaUpdateView.as_view(), name='editar_multa'),
  path('gerenciar/multas/excluir/<int:pk>/', MultaDeleteView.as_view(), name='excluir_multa'),
  path('gerenciar/emprestimos/', EmprestimoListView.as_view(), name='lista_emprestimos'),
  path('gerenciar/emprestimos/devolver/<int:pk>/', registrar_devolucao, name='registrar_devolucao'),
  path('gerenciar/emprestimos/dano/<int:pk>/', registrar_dano, name='registrar_dano'),
  path('gerenciar/emprestimos/renovar/<int:pk>/', renovar_emprestimo, name='renovar_emprestimo'),
  path('gerenciar/estoque/', ExemplarListView.as_view(), name='lista_exemplares'),
  path('gerenciar/estoque/novo/', ExemplarCreateView.as_view(), name='cadastro_exemplar'),
  path('gerenciar/estoque/editar/<int:pk>/', ExemplarUpdateView.as_view(), name='editar_exemplar'),
  path('gerenciar/estoque/excluir/<int:pk>/', ExemplarDeleteView.as_view(), name='excluir_exemplar'),
  path('gerenciar/recursos/', RecursoGerenciarListView.as_view(), name='lista_recursos_crud'),
  path('gerenciar/recursos/novo/', RecursoCreateView.as_view(), name='cadastro_recurso'),
  path('gerenciar/recursos/editar/<int:pk>/', RecursoUpdateView.as_view(), name='editar_recurso'),
  path('gerenciar/recursos/excluir/<int:pk>/', RecursoDeleteView.as_view(), name='excluir_recurso'),
  path('gerenciar/reservas/confirmar/<int:pk>/', confirmar_emprestimo, name='confirmar_emprestimo'),
  path('reserva-futura/<int:pk>/', reserva_futura, name='reserva_futura'), 
]




