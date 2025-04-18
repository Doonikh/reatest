import requests
from django.conf import settings

def send_new_ticket_notification(ticket, request):
    """
    Отправляет уведомление о новой заявке в Telegram в чат TELEGRAM_NEW_TICKETS_CHAT_ID.
    """
    message_text = (
        f"<b>Новая заявка!</b>\n"
        f"<b>Дата:</b> {ticket.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"<b>ФИО:</b> {ticket.full_name}\n"
        f"<b>Телефон:</b> {ticket.phone}\n"
        f"<b>Внутренний номер:</b> {ticket.internal_phone or 'N/A'}\n"
        f"<b>Корпус:</b> {ticket.building}\n"
        f"<b>Кабинет:</b> {ticket.office}\n"
        f"<b>Описание проблемы:</b> {ticket.error_description}\n"
    )
    if ticket.images.exists():
        image_url = request.build_absolute_uri(ticket.images.first().image.url)
        message_text += f"<b>Фото:</b> {image_url}\n"

    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    new_chat_id = getattr(settings, 'TELEGRAM_NEW_TICKETS_CHAT_ID', None)
    if not bot_token or not new_chat_id:
        return False

    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': new_chat_id,
        'text': message_text,
        'parse_mode': 'HTML'
    }
    response = requests.post(send_url, data=params)
    return response.status_code == 200
