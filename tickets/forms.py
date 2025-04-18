from django import forms
from .models import Ticket
from django.utils.translation import gettext as _


class TicketForm(forms.ModelForm):
    internal_phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Введите внутренний номер')}),
        required=False,
        label=_('Внутренний номер телефона')
    )

    class Meta:
        model = Ticket
        fields = ['full_name', 'email', 'phone', 'internal_phone', 'building', 'office', 'error_description']

    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'phone-mask', 'placeholder': _('Введите номер телефона')}),
        label=_('Телефон')
    )
