from django.contrib import admin

from .models import (
    Recursos,
    Tipos,
    Subtipos,
    Exemplares,
    Emprestimos,
    Reservas,
    Renovacoes,
    Multas
)

class RecursosAdmin(admin.ModelAdmin):
  
  list_display = (
      'id', 
      'descricao', 
      'tipo', 
      'subtipo', 
      'quantidade_total', 
      'valor_emprestimo_diaria',
      'max_dias_emprestimo',
      'permite_renovacao',
      'multa_atraso_multiplicador',
      'multa_dano_multiplicador'
    )


class ExemplaresAdmin(admin.ModelAdmin):
    list_display = ('recurso', 'status', 'data_aquisicao')
    

admin.site.register(Recursos,RecursosAdmin)
admin.site.register(Tipos)
admin.site.register(Subtipos)
admin.site.register(Exemplares,ExemplaresAdmin)
admin.site.register(Emprestimos)
admin.site.register(Reservas)
admin.site.register(Renovacoes)
admin.site.register(Multas)