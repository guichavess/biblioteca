from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse 
from .models import Recursos,Subtipos,Reservas,Emprestimos,Exemplares, Multas, Renovacoes
from django.views.generic import TemplateView,ListView, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from usuarios.models import Clientes
from django.contrib.auth.decorators import login_required 
from django.db import transaction 
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse_lazy
from datetime import date
from datetime import timedelta
from .forms import ExemplarCreateForm, ExemplarUpdateForm
from django.db.models import Min



CAMPOS_RECURSO = [
    'tipo', 
    'subtipo', 
    'descricao', 
    'quantidade_total', 
    'valor_emprestimo_diaria', 
    'max_dias_emprestimo', 
    'permite_renovacao', 
    'multa_atraso_multiplicador', 
    'multa_dano_multiplicador',
    'imagem_capa' 
]

class RecursoGerenciarListView(LoginRequiredMixin, ListView):
    model = Recursos
    template_name = 'recursos/gerenciar_recursos.html'
    context_object_name = 'recursos'
    paginate_by = 15



    def get_queryset(self):
        queryset = super().get_queryset().select_related('subtipo').order_by('descricao')
        query = self.request.GET.get('q')
        subtipo_id = self.request.GET.get('subtipo')

        if query:
            queryset = queryset.filter(descricao__icontains=query)
        if subtipo_id:
            queryset = queryset.filter(subtipo_id=subtipo_id)
            
        return queryset



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lista_de_subtipos'] = Subtipos.objects.all().order_by('nome_subtipo')
        return context
    


class RecursoCreateView(LoginRequiredMixin, CreateView):
    model = Recursos
    template_name = 'recursos/recurso_form.html'
    fields = CAMPOS_RECURSO
    success_url = reverse_lazy('recursos:lista_recursos_crud')


class RecursoUpdateView(LoginRequiredMixin, UpdateView):
    model = Recursos
    template_name = 'recursos/recurso_form.html'
    fields = CAMPOS_RECURSO
    

    def get_success_url(self):
        page = self.request.GET.get('page')
        base_url = reverse_lazy('recursos:lista_recursos_crud')
        if page:
            return f"{base_url}?page={page}"
        return base_url


class RecursoDeleteView(LoginRequiredMixin, DeleteView):
    model = Recursos
    template_name = 'recursos/recurso_confirm_delete.html'
    success_url = reverse_lazy('recursos:lista_recursos_crud')


class Inicio(LoginRequiredMixin,ListView):
  template_name = "inicio.html"
  model = Subtipos
  context_object_name = "lista_subtipos"


class Recurso(LoginRequiredMixin,ListView):
  template_name = 'recursos/recurso.html' 
  model = Recursos
  context_object_name = 'recursos'


  def get_queryset(self):
    subtipo_url_id = self.kwargs['pk']
    queryset = Recursos.objects.filter(subtipo_id=subtipo_url_id)
    return queryset


  def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          subtipo_url_id = self.kwargs['pk']
          context['subtipo'] = get_object_or_404(Subtipos, pk=subtipo_url_id)
          return context




def criar_reserva(request, pk):
  recurso = get_object_or_404(Recursos, pk=pk)
  
  if recurso.get_qtd_disponivel() <= 0:
    return redirect('recursos:reserva_futura', pk=recurso.pk)
  
  reserva = request.session.get('reserva', {})
  recurso_id = str(recurso.id)
  if recurso_id not in reserva:
      reserva[recurso_id] = {
          'id': recurso.id,
          'descricao': recurso.descricao,
          'valor_diaria': float(recurso.valor_emprestimo_diaria),
        }
      messages.success(request, f"Recurso '{recurso.descricao}' adicionado à sua reserva.")
  else:
      messages.info(request, f"O recurso '{recurso.descricao}' já estava na sua reserva.")

  request.session['reserva'] = reserva
  return redirect(request.META.get('HTTP_REFERER', 'recurso'))


@login_required
def reserva_futura(request, pk):
    recurso = get_object_or_404(Recursos, pk=pk)
    
    if request.method == 'POST':
        data_escolhida_str = request.POST.get('data_reserva')
        cliente_id = request.POST.get('cliente_id')

        if not data_escolhida_str or not cliente_id:
            messages.error(request, "Por favor, selecione um cliente e uma data.")
            return redirect('recursos:reserva_futura', pk=recurso.pk)

        data_escolhida = date.fromisoformat(data_escolhida_str)
        cliente = get_object_or_404(Clientes, pk=cliente_id)
        Reservas.objects.create(
            cliente=cliente,
            recurso=recurso,
            data_reserva=timezone.now(),
            data_inicio_reserva=data_escolhida,
            status='ativa'
        )

        messages.success(request, f"Recurso '{recurso.descricao}' reservado para {data_escolhida.strftime('%d/%m/%Y')}.")
        return redirect('recursos:lista_recursos', pk=recurso.subtipo_id)


    else:
        prox_data = proxima_data_disponivel(recurso.id)
        context = {
            'recurso': recurso,
            'clientes': Clientes.objects.all(),
            'proxima_data_sugerida': prox_data.isoformat()
        }
        return render(request, 'reservas/reserva_futura.html', context)



def detalhes_reserva(request):
  reserva = request.session.get('reserva', {})
  itens_reserva = reserva.values()
  clientes = Clientes.objects.all()
  context = {
    'itens_reserva': itens_reserva,
    'clientes': clientes
    }

  return render(request, 'reservas/reserva.html', context)


def remover_recurso(request, pk):
    reserva = request.session.get('reserva', {})
    recurso_id = str(pk)
    if recurso_id in reserva:
        del reserva[recurso_id]
        messages.success(request, 'Item removido da reserva.')
    request.session['reserva'] = reserva
    return redirect('recursos:detalhes_reserva')


@login_required 
@transaction.atomic 
def finalizar_reserva(request):
    if request.method == 'POST':
        reserva = request.session.get('reserva', {})
        cliente_id = request.POST.get('cliente_id')

        if not reserva:
            messages.error(request, 'Sua Reserva está vazio.')
            return redirect('recursos:detalhes_reserva')
    
        if not cliente_id:
            messages.error(request, 'Você precisa selecionar um cliente.')
            return redirect('recursos:detalhes_reserva')
        
        try:
            cliente = Clientes.objects.get(pk=cliente_id)
        except Clientes.DoesNotExist:
            messages.error(request, 'Cliente não encontrado.')
            return redirect('recursos:detalhes_reserva')

        for item_id, item_info in reserva.items():
            recurso = get_object_or_404(Recursos, pk=item_info['id'])
            exemplar_disponivel = Exemplares.objects.filter(recurso=recurso, status='disponivel').first()
            
            if exemplar_disponivel:
                Reservas.objects.create(
                    cliente=cliente,
                    recurso=recurso,
                    data_reserva=timezone.now(),
                    status='ativa'
                )

                exemplar_disponivel.status = 'reservado'
                exemplar_disponivel.save()
            
            else:
                
                messages.error(request, f"Desculpe, o item '{recurso.descricao}' não está mais disponível.")
                return redirect('recursos:detalhes_reserva')

        request.session['reserva'] = {}
        messages.success(request, 'Reserva(s) realizada(s) com sucesso!')
        return redirect('recursos:inicio')

    else:
        return redirect('recursos:detalhes_reserva')


class ReservaListView(LoginRequiredMixin, ListView):
    model = Reservas
    template_name = 'reservas/gerenciar_reservas.html'
    context_object_name = 'reservas'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente', 'recurso').order_by('-data_reserva')
        query = self.request.GET.get('q')
        status = self.request.GET.get('status')

        if query:
            queryset = queryset.filter(cliente__nome__icontains=query)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pega os status únicos que existem no banco para o filtro
        context['lista_de_status'] = Reservas.objects.values_list('status', flat=True).distinct()
        return context


class ReservaUpdateView(LoginRequiredMixin, UpdateView):
    model = Reservas
    template_name = 'reservas/reserva_form.html'
    fields = ['status'] 
    
    def get_success_url(self):
        page = self.request.GET.get('page')
        base_url = reverse_lazy('recursos:lista_reservas')
        if page:
            return f"{base_url}?page={page}"
        return base_url



class ReservaDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservas
    template_name = 'reservas/reserva_confirm_delete.html' 
    success_url = reverse_lazy('recursos:lista_reservas')


    def post(self, request, *args, **kwargs):
        try:
            
            reserva = self.get_object()
            
            exemplar_a_liberar = Exemplares.objects.filter(
                recurso=reserva.recurso, 
                status='reservado'
            ).first() 
            
            if exemplar_a_liberar:
                exemplar_a_liberar.status = 'disponivel' 
                exemplar_a_liberar.save()
        
        except Exemplares.DoesNotExist:
             pass
        return super().delete(request, *args, **kwargs)
    


class MultaListView(LoginRequiredMixin, ListView):
    model = Multas
    template_name = 'multas/gerenciar_multas.html'
    context_object_name = 'multas'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('emprestimo__cliente').order_by('-id')
        query = self.request.GET.get('q')
        tipo_multa = self.request.GET.get('tipo_multa')
        paga = self.request.GET.get('paga')

        if query:
            queryset = queryset.filter(emprestimo__cliente__nome__icontains=query)
        if tipo_multa:
            queryset = queryset.filter(tipo_multa=tipo_multa)
        if paga in ['0', '1']:
            queryset = queryset.filter(paga=paga)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lista_tipos_multa'] = Multas.objects.values_list('tipo_multa', flat=True).distinct()
        context['status_pagamento'] = [{'value': '1', 'display': 'Sim'}, {'value': '0', 'display': 'Não'}]
        return context
    



class MultaUpdateView(LoginRequiredMixin, UpdateView):
    model = Multas
    template_name = 'multas/multa_form.html'
    fields = ['paga', 'tipo_multa', 'valor_multa']
    
    def get_success_url(self):
        page = self.request.GET.get('page')
        base_url = reverse_lazy('recursos:lista_multas')
        if page:
            return f"{base_url}?page={page}"
        return base_url


class MultaDeleteView(LoginRequiredMixin, DeleteView):
    model = Multas
    template_name = 'multas/multa_confirm_delete.html' 
    success_url = reverse_lazy('recursos:lista_multas')




class EmprestimoListView(LoginRequiredMixin, ListView):
    model = Emprestimos
    template_name = 'emprestimos/gerenciar_emprestimos.html'
    context_object_name = 'emprestimos'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente', 'exemplar__recurso').order_by('-data_emprestimo')
        query = self.request.GET.get('q')
        status = self.request.GET.get('status')

        if query:
            queryset = queryset.filter(cliente__nome__icontains=query)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lista_de_status'] = Emprestimos.objects.values_list('status', flat=True).distinct()
        return context




class ExemplarListView(LoginRequiredMixin, ListView):
    model = Exemplares
    template_name = 'exemplares/gerenciar_exemplares.html' 
    context_object_name = 'exemplares' 
    paginate_by = 15 
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('recurso')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        recurso_id = self.request.GET.get('recurso')
        if recurso_id:
            queryset = queryset.filter(recurso_id=recurso_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lista_de_recursos'] = Recursos.objects.all().order_by('descricao')
        context['lista_de_status'] = Exemplares.STATUS_CHOICES
        return context
    


class ExemplarCreateView(LoginRequiredMixin, CreateView):
    model = Exemplares
    template_name = 'exemplares/exemplar_form.html'
    form_class = ExemplarCreateForm
    success_url = reverse_lazy('recursos:lista_exemplares')
    


class ExemplarUpdateView(LoginRequiredMixin, UpdateView):
    model = Exemplares
    template_name = 'exemplares/exemplar_form.html'
    form_class = ExemplarUpdateForm 


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.request.GET.get('page', '')
        return context

    def get_success_url(self):
        page = self.request.POST.get('page')
        base_url = reverse_lazy('recursos:lista_exemplares')
        if page:
            return f"{base_url}?page={page}"
        return base_url


class ExemplarDeleteView(LoginRequiredMixin, DeleteView):
    model = Exemplares
    template_name = 'exemplares/exemplar_confirm_delete.html' 
    success_url = reverse_lazy('recursos:lista_exemplares')



@login_required
@transaction.atomic
def registrar_devolucao(request, pk):
    emprestimo = get_object_or_404(Emprestimos, pk=pk)
    
    if emprestimo.status == 'devolvido':
        messages.error(request, 'Este item já foi devolvido.')
        return redirect('recursos:lista_emprestimos')

    emprestimo.status = 'devolvido'
    emprestimo.data_devolucao_efetiva = timezone.now()
    emprestimo.save()

    exemplar = emprestimo.exemplar
    if exemplar.status != 'danificado':
      exemplar.status = 'disponivel'
      exemplar.save()

    data_hoje = date.today()
    if data_hoje > emprestimo.data_prevista_devolucao:
        recurso = exemplar.recurso
        valor_diaria = recurso.valor_emprestimo_diaria
        dias_atraso = (data_hoje - emprestimo.data_prevista_devolucao).days
        valor_multa_calculada = (recurso.multa_atraso_multiplicador * valor_diaria) * dias_atraso
        
        Multas.objects.create(
            emprestimo=emprestimo,
            tipo_multa='atraso',
            valor_multa=valor_multa_calculada,
            paga=0
        )
        messages.warning(request, f'Devolução registrada com {dias_atraso} dia(s) de ATRASO. Multa de R$ {valor_multa_calculada} gerada.')
    
    else:
        messages.success(request, 'Devolução registrada no prazo. Exemplar devolvido ao estoque.')

    return redirect('recursos:lista_emprestimos')



@login_required
@transaction.atomic
def confirmar_emprestimo(request, pk):
    reserva = get_object_or_404(Reservas, pk=pk)
    recurso = reserva.recurso
    data_hoje = timezone.now().date()
    
    if reserva.status != 'ativa':
        messages.error(request, 'Esta reserva não está mais ativa.')
        return redirect('recursos:lista_reservas')

    
    is_media = recurso.max_dias_emprestimo is not None

    if request.method == 'POST':
        data_devolucao_final = None
        if is_media:
            data_devolucao_final = data_hoje + timedelta(days=recurso.max_dias_emprestimo)
        else:
            data_form_str = request.POST.get('data_devolucao')
            if not data_form_str:
                messages.error(request, 'Para impressos, você deve informar a data de devolução.')
                context = {'reserva': reserva, 'is_media': is_media}
                # --- CORREÇÃO ---
                return render(request, 'emprestimos/confirmar_emprestimo_form.html', context)
            
            data_devolucao_final = date.fromisoformat(data_form_str)

            if data_devolucao_final <= data_hoje:
                messages.error(request, 'A data de devolução deve ser no futuro.')
                context = {'reserva': reserva, 'is_media': is_media}
                # --- CORREÇÃO ---
                return render(request, 'emprestimos/confirmar_emprestimo_form.html', context)

        
        try:
            exemplar = Exemplares.objects.filter(recurso=recurso, status='reservado').first()
            if not exemplar:
                exemplar = Exemplares.objects.filter(recurso=recurso, status='disponivel').first()
            if not exemplar:
                raise Exemplares.DoesNotExist
        except Exemplares.DoesNotExist:
            messages.error(request, f"Nenhum exemplar de '{recurso.descricao}' está disponível.")
            return redirect('recursos:lista_reservas')
        Emprestimos.objects.create(
            cliente=reserva.cliente,
            exemplar=exemplar,
            data_emprestimo=timezone.now(),
            data_prevista_devolucao=data_devolucao_final, 
            status='ativo'
        )

        exemplar.status = 'emprestado'
        exemplar.save()

        reserva.status = 'atendida'
        reserva.save()

        messages.success(request, f"Empréstimo de '{exemplar.recurso.descricao}' registrado.")
        return redirect('recursos:lista_reservas')

    else:
        context = {
            'reserva': reserva,
            'is_media': is_media
        }
        
        if is_media:
            context['data_devolucao_prevista'] = data_hoje + timedelta(days=recurso.max_dias_emprestimo)
        
        # --- CORREÇÃO ---
        return render(request, 'emprestimos/confirmar_emprestimo_form.html', context)





@login_required
@transaction.atomic
def registrar_dano(request, pk):
    emprestimo = get_object_or_404(Emprestimos, pk=pk)
    
    if emprestimo.status != 'ativo':
        messages.error(request, 'Apenas empréstimos ativos podem ser registrados como danificados.')
        return redirect('recursos:lista_emprestimos')

    recurso = emprestimo.exemplar.recurso
    
    valor_diaria = recurso.valor_emprestimo_diaria
    valor_multa_calculada = recurso.multa_dano_multiplicador * valor_diaria

    Multas.objects.create(
        emprestimo=emprestimo,
        tipo_multa='dano',
        valor_multa=valor_multa_calculada,
        paga=0
    )

    exemplar = emprestimo.exemplar
    exemplar.status = 'danificado'
    exemplar.save()

    valor_multa_formatado = f'{valor_multa_calculada:.2f}'.replace('.', ',')
    messages.warning(request, f'Multa por DANO de R$ {valor_multa_formatado} registrada. O exemplar foi removido do estoque (danificado).')
    
    return redirect('recursos:lista_emprestimos')


@login_required
@transaction.atomic
def renovar_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimos, pk=pk)
    recurso = emprestimo.exemplar.recurso

    if emprestimo.status != 'ativo':
        messages.error(request, 'Apenas empréstimos ativos podem ser renovados.')
        return redirect('recursos:lista_emprestimos')

    if not recurso.permite_renovacao:
        messages.error(request, f'O recurso "{recurso.descricao}" não permite renovação.')
        return redirect('recursos:lista_emprestimos')

    reservas_ativas = Reservas.objects.filter(recurso=recurso, status='ativa').exists()
    if reservas_ativas:
        messages.error(request, f'Não é possível renovar: O recurso "{recurso.descricao}" possui reservas ativas.')
        return redirect('recursos:lista_emprestimos')
    
    if request.method == 'POST':
        data_form_str = request.POST.get('data_devolucao')
        
        if not data_form_str:
            messages.error(request, 'Você deve informar a nova data de devolução.')
            context = {'emprestimo': emprestimo}
            return render(request, 'emprestimos/renovar_emprestimo_form.html', context)
        
        nova_data_devolucao = date.fromisoformat(data_form_str)

        if nova_data_devolucao <= emprestimo.data_prevista_devolucao:
            messages.error(request, f'A nova data deve ser posterior à data de devolução atual ({emprestimo.data_prevista_devolucao.strftime("%d/%m/%Y")}).')
            context = {'emprestimo': emprestimo}
            return render(request, 'emprestimos/renovar_emprestimo_form.html', context)

        Renovacoes.objects.create(
            emprestimo=emprestimo,
            data_renovacao=timezone.now(),
            nova_data_prevista_devolucao=nova_data_devolucao
        )

        emprestimo.data_prevista_devolucao = nova_data_devolucao
        emprestimo.save()

        messages.success(request, f"Empréstimo renovado com sucesso. Nova data de devolução: {nova_data_devolucao.strftime('%d/%m/%Y')}")
        return redirect('recursos:lista_emprestimos')

    else:
        context = {
            'emprestimo': emprestimo
        }
        return render(request, 'emprestimos/renovar_emprestimo_form.html', context)
    


def proxima_data_disponivel(recurso_id):
    hoje = timezone.now().date()
    proximo_emprestimo_devolucao = Emprestimos.objects.filter(
        exemplar__recurso_id=recurso_id, 
        status='ativo'
    ).aggregate(min_data=Min('data_prevista_devolucao'))['min_data']

    proxima_reserva_inicio = Reservas.objects.filter(
        recurso_id=recurso_id, 
        status='ativa'
    ).aggregate(min_data=Min('data_inicio_reserva'))['min_data']

    datas = [d for d in [proximo_emprestimo_devolucao, proxima_reserva_inicio] if d is not None]

    if not datas:
        return hoje + timedelta(days=1)
    return max(datas) + timedelta(days=1)