def reserva_context(request):
    reserva = request.session.get('reserva', {})
    contagem_reserva = len(reserva)
    
    return {
        'contagem_reserva': contagem_reserva
    }