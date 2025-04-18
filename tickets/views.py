# tickets/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TicketForm
from .models import Ticket, TicketImage
from .telegram_utils import send_new_ticket_notification  # Импорт из нового модуля

def create_ticket(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            if request.user.is_authenticated:
                ticket.created_by = request.user
            ticket.save()

            # Обработка изображений
            image_files = request.FILES.getlist('image')
            for image_file in image_files:
                TicketImage.objects.create(ticket=ticket, image=image_file)

            # Отправляем уведомление о новой заявке в Telegram
            send_new_ticket_notification(ticket, request)

            return redirect('ticket_success')
    else:
        ticket_form = TicketForm()

    return render(request, 'tickets/create_ticket.html', {'ticket_form': ticket_form})

def ticket_display(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    stats = {
        'in_progress': tickets.filter(status__iexact='in_progress').count(),
        'closed':      tickets.filter(status__iexact='closed').count(),
        'new':         tickets.filter(status__iexact='new').count(),
        'denied':      tickets.filter(status__iexact='denied').count(),
    }
    return render(request, 'tickets/ticket_display.html', {'tickets': tickets, 'stats': stats})

def ticket_list_partial(request):
    """
    Частичное представление списка заявок (для обновления AJAX каждые 15 секунд).
    """
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'tickets/ticket_list_partial.html', {'tickets': tickets})

def ticket_success(request):
    return render(request, 'tickets/ticket_success.html')

def public_ticket_images(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    images = ticket.images.all()
    return render(request, 'tickets/public_ticket_images.html', {'ticket': ticket, 'images': images})
