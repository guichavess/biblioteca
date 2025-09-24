from django.db import models


# Create your models here.
class Clientes(models.Model):
    cpf = models.CharField(unique=True, max_length=14)
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True, max_length=255, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clientes'