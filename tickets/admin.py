from django.contrib import admin, messages
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, get_object_or_404, redirect
import requests
from django.conf import settings
from django.utils.safestring import mark_safe
from .models import Ticket, TicketImage

class TicketImageInline(admin.TabularInline):
    model = TicketImage
    extra = 0
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width:200px; max-height:200px;"/></a>',
                obj.image.url,
                obj.image.url
            )
        return ""
    image_tag.short_description = 'Фото'

class TicketAdmin(admin.ModelAdmin):
    change_list_template = "admin/tickets/ticket/change_list.html"
    list_display = (
        'ticket_number', 'created_at_formatted', 'location', 'task_summary', 'contact_info',
        'status', 'done_by', 'has_images', 'send_to_telegram'
    )
    list_editable = ('done_by', 'status')
    list_filter = ('status', 'building', 'done_by')
    search_fields = ('full_name', 'phone', 'email')
    ordering = ('-created_at',)
    inlines = [TicketImageInline]

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)
        stats = {
            'new': {
                'label': 'Новая',
                'count': qs.filter(status='new').count(),
                'color': '#ffe0e0',
            },
            'in_progress': {
                'label': 'В работе',
                'count': qs.filter(status='in_progress').count(),
                'color': '#faffc3',
            },
            'closed': {
                'label': 'Выполнено',
                'count': qs.filter(status='closed').count(),
                'color': '#e0ffe0',
            },
            'denied': {
                'label': 'Отклонена',
                'count': qs.filter(status='denied').count(),
                'color': '#a7d7ff',
            },
        }
        extra_context = extra_context or {}
        extra_context['ticket_stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if obj.done_by and obj.status == 'new':
            obj.status = 'in_progress'
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:ticket_id>/images/', self.admin_site.admin_view(self.ticket_images_view),
                 name='tickets_ticket_images'),
            path('<int:ticket_id>/send_to_telegram/', self.admin_site.admin_view(self.send_to_telegram_view),
                 name='tickets_send_to_telegram'),
        ]
        return custom_urls + urls

    def ticket_images_view(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        images = ticket.images.all()
        context = dict(
            self.admin_site.each_context(request),
            ticket=ticket,
            images=images,
            opts=self.model._meta,
        )
        return render(request, 'admin/tickets/ticket/ticket_images.html', context)

    def send_to_telegram_view(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        message_text = (
            f"<b>Дата:</b> {ticket.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"<b>ФИО:</b> {ticket.full_name}\n"
            f"<b>Телефон:</b> {ticket.phone}\n"
            f"<b>Внутренний номер:</b> {ticket.internal_phone or 'N/A'}\n"
            f"<b>Корпус:</b> {ticket.building}\n"
            f"<b>Кабинет:</b> {ticket.office}\n"
            f"<b>Суть задачи:</b> {ticket.error_description}\n"
        )
        if ticket.images.exists():
            image_url = request.build_absolute_uri(ticket.images.first().image.url)
            message_text += f"<b>Фото:</b> {image_url}\n"

        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        if not bot_token or not chat_id:
            messages.error(request, "Настройки Telegram бота не сконфигурированы.")
            return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {
            'chat_id': chat_id,
            'text': message_text,
            'parse_mode': 'HTML'
        }
        response = requests.post(send_url, data=params)
        if response.status_code == 200:
            messages.success(request, "Сообщение отправлено в Telegram!")
        else:
            messages.error(request, "Ошибка отправки сообщения в Telegram.")
        return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

    def send_to_telegram(self, obj):
        url = reverse('admin:tickets_send_to_telegram', args=[obj.pk])
        svg_icon = mark_safe(
            '''
            <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="24" height="24" viewBox="0 0 48 48">
                <path fill="#29b6f6" d="M24 4A20 20 0 1 0 24 44A20 20 0 1 0 24 4Z"></path>
                <path fill="#fff" d="M33.95,15l-3.746,19.126c0,0-0.161,0.874-1.245,0.874c-0.576,0-0.873-0.274-0.873-0.274l-8.114-6.733
                l-3.97-2.001l-5.095-1.355c0,0-0.907-0.262-0.907-1.012c0-0.625,0.933-0.923,0.933-0.923l21.316-8.468
                c-0.001-0.001,0.651-0.235,1.126-0.234C33.667,14,34,14.125,34,14.5C34,14.75,33.95,15,33.95,15z"></path>
                <path fill="#b0bec5" d="M23,30.505l-3.426,3.374c0,0-0.149,0.115-0.348,0.12c-0.069,0.002-0.143-0.009-0.219-0.043
                l0.964-5.965L23,30.505z"></path>
                <path fill="#cfd8dc" d="M29.897,18.196c-0.169-0.22-0.481-0.26-0.701-0.093L16,26c0,0,2.106,5.892,2.427,6.912
                c0.322,1.021,0.58,1.045,0.58,1.045l0.964-5.965l9.832-9.096C30.023,18.729,30.064,18.416,29.897,18.196z"></path>
            </svg>
            '''
        )
        return format_html('<a class="btn btn-telegram" href="{}">{}</a>', url, svg_icon)
    send_to_telegram.short_description = 'Отправить в Telegram'

    def ticket_number(self, obj):
        return obj.pk
    ticket_number.short_description = 'Номер'

    def created_at_formatted(self, obj):
        return format_html(
            "<div>{}</div><div style='font-size:90%; color:#555;'>{}</div>",
            obj.created_at.strftime("%d.%m.%Y"),
            obj.created_at.strftime("%H:%M")
        )
    created_at_formatted.short_description = "Дата создания"

    def location(self, obj):
        return format_html(
            "<div>{}</div><div style='font-size:90%; color:#555;'>{}</div>",
            obj.building,
            obj.office
        )
    location.short_description = "Расположение"

    def task_summary(self, obj):
        return obj.error_description
    task_summary.short_description = "Суть задачи"

    def contact_info(self, obj):
        return format_html(
            "<div>{}</div><div style='font-size:90%; color:#555;'>{}</div>",
            obj.internal_phone,
            self.full_name_formatted(obj)
        )
    contact_info.short_description = "Контакт"

    def full_name_formatted(self, obj):
        full_name = obj.full_name.split()
        if len(full_name) == 3:
            return f"{full_name[0]} {full_name[1][0]}.{full_name[2][0]}."
        return obj.full_name
    full_name_formatted.short_description = 'ФИО'

    def done_by(self, obj):
        return obj.done_by.get_full_name() if obj.done_by else "Не указано"
    done_by.short_description = 'Исполнитель'

    def has_images(self, obj):
        if obj.images.exists():
            url = reverse('admin:tickets_ticket_images', args=[obj.pk])
            svg_img = mark_safe('''
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 40 40">
                    <path fill="#fff" d="M1.5 4.5H38.5V35.5H1.5z"></path>
                    <path fill="#788b9c" d="M38,5v30H2V5H38 M39,4H1v32h38V4L39,4z"></path>
                    <path fill="#b5deff" d="M6 9H34V26.875H6z"></path>
                    <path fill="#d9f6ff" d="M6 19H34V27H6z"></path>
                    <path fill="#7aadf0" d="M6 27H34V31H6z"></path>
                    <path fill="#d9f6ff" d="M14.75 15A3.5 3.143 0 1 0 14.75 21.286A3.5 3.143 0 1 0 14.75 15Z"></path>
                    <path fill="#d9f6ff" d="M11.25 15.786000000000001A2.625 2.357 0 1 0 11.25 20.5 2.625 2.357 0 1 0 11.25 15.786000000000001zM20 16.570999999999998A3.5 3.143 0 1 0 20 22.857 3.5 3.143 0 1 0 20 16.570999999999998z"></path>
                    <path fill="#d9f6ff" d="M25.25 15A3.5 3.143 0 1 0 25.25 21.286 3.5 3.143 0 1 0 25.25 15zM32.25 16.572A1.75 1.571 0 1 0 32.25 19.714000000000002 1.75 1.571 0 1 0 32.25 16.572zM7.75 16.572A1.75 1.571 0 1 0 7.75 19.714000000000002 1.75 1.571 0 1 0 7.75 16.572z"></path>
                    <path fill="#d9f6ff" d="M28.75 15.786000000000001A2.625 2.357 0 1 0 28.75 20.5A2.625 2.357 0 1 0 28.75 15.786000000000001Z"></path>
                    <path fill="#4a6d9c" d="M6 27L34 27 34 25.384 25.25 20z"></path>
                    <path fill="#5d84b8" d="M27 27L6 27 6 23 14.75 19z"></path>
                </svg>
            ''')
            return format_html('<a href="{}">{}</a>', url, svg_img)
        else:
            return format_html('<span style="color: red;">Нет</span>')
    has_images.short_description = 'Прикрепленные фото'

    class Media:
        js = ('tickets/js/ticket_admin.js',)
        css = {
            'all': ('tickets/css/ticket_admin.css',)
        }

admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketImage)
