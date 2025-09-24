from django.db import models
from django.utils import timezone

opcoes = (
    ("disponível","Disponível"),
    ("inidsponivel", "Indisponível")
)


class Emprestimos(models.Model):
    cliente = models.ForeignKey('usuarios.Clientes', models.DO_NOTHING)
    exemplar = models.ForeignKey('Exemplares', models.DO_NOTHING)
    data_emprestimo = models.DateTimeField()
    data_prevista_devolucao = models.DateField()
    data_devolucao_efetiva = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        db_table = 'emprestimos'


class Exemplares(models.Model):
    
    STATUS_CHOICES = (
        ('disponivel', 'Disponível'), 
        ('reservado', 'Reservado'),   
        ('emprestado', 'Emprestado'),
        ('danificado', 'Danificado'), 
    )

    recurso = models.ForeignKey('Recursos', models.DO_NOTHING)
    
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='disponivel',
        blank=True, null=True
    )
    data_aquisicao = models.DateField(blank=True, null=True)

    class Meta:
        
        db_table = 'exemplares'


class Multas(models.Model):
    emprestimo = models.ForeignKey(Emprestimos, models.DO_NOTHING)
    tipo_multa = models.CharField(max_length=10)
    valor_multa = models.DecimalField(max_digits=10, decimal_places=2)
    paga = models.IntegerField(blank=True, null=True)

    

    class Meta:
        
        db_table = 'multas'


class Recursos(models.Model):
    tipo = models.ForeignKey('Tipos', models.DO_NOTHING)
    subtipo = models.ForeignKey('Subtipos', models.DO_NOTHING)
    descricao = models.CharField(max_length=255)
    quantidade_total = models.IntegerField()
    valor_emprestimo_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    max_dias_emprestimo = models.IntegerField(null=True, blank=True, default=None)
    permite_renovacao = models.BooleanField(default=True)
    multa_atraso_multiplicador = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    multa_dano_multiplicador = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    imagem_capa = models.ImageField(upload_to='recurso_capas/', blank=True, null=True)

    def get_qtd_disponivel(self):
        """
        Conta quantos exemplares deste recurso estão com status 'disponivel'.
        """
        return self.exemplares_set.filter(status='disponivel').count()

    def __str__(self):
        return self.descricao

    class Meta:
        
        db_table = 'recursos'


class Renovacoes(models.Model):
    emprestimo = models.ForeignKey(Emprestimos, models.DO_NOTHING)
    data_renovacao = models.DateTimeField(blank=True, null=True)
    nova_data_prevista_devolucao = models.DateField()

    class Meta:
        
        db_table = 'renovacoes'


class Reservas(models.Model):
    cliente = models.ForeignKey('usuarios.Clientes', models.DO_NOTHING)
    recurso = models.ForeignKey(Recursos, models.DO_NOTHING)
    data_reserva = models.DateTimeField(blank=True, null=True)
    data_inicio_reserva = models.DateField(default=timezone.now)
    status = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        
        db_table = 'reservas'


class Subtipos(models.Model):
    tipo = models.ForeignKey('Tipos', models.DO_NOTHING)
    nome_subtipo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='subtipo_imagens/', blank=True, null=True)

    def __str__(self):
        return self.nome_subtipo

    class Meta:
        
        db_table = 'subtipos'


class Tipos(models.Model):
    nome_tipo = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.nome_tipo
    
    class Meta:
        
        db_table = 'tipos'
