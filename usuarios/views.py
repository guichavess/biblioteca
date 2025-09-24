from django.shortcuts import render
from .models import Clientes
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .forms import ClienteForm



class ClienteListView(LoginRequiredMixin, ListView):
    model = Clientes
    template_name = 'gerenciar_clientes.html' 
    context_object_name = 'clientes'
    paginate_by = 15


    def get_queryset(self):
            queryset = super().get_queryset().order_by('nome') 
            query = self.request.GET.get('q')
            
            if query:
                queryset = queryset.filter(
                    Q(nome__icontains=query) |
                    Q(cpf__icontains=query) |
                    Q(email__icontains=query)
                )
            return queryset


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Clientes
    template_name = 'cadastro_cliente.html'
    form_class = ClienteForm  
    success_url = reverse_lazy('usuarios:lista_clientes')


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Clientes
    template_name = 'cadastro_cliente.html'
    form_class = ClienteForm 



    def get_success_url(self):
        page = self.request.GET.get('page')
        base_url = reverse_lazy('usuarios:lista_clientes')
        
        if page:
            return f"{base_url}?page={page}"
        
        return base_url


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Clientes
    template_name = 'delete_cliente.html' 
    success_url = reverse_lazy('usuarios:lista_clientes')