from django import forms

class DailyPlanShareForm(forms.Form):
    recipient_email = forms.EmailField(label="Email del destinatario")

class MealShareForm(forms.Form):
    recipient_email = forms.EmailField(label="Email del destinatario")

