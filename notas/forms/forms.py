from django import forms

class DailyPlanShareForm(forms.Form):
    recipient_email = forms.EmailField(label="Email del destinatario")

class MealShareForm(forms.Form):
    recipient_email = forms.EmailField(label="Email del destinatario")


from notas.models import Food

class FoodEditForm(forms.ModelForm):

    class Meta:
        model = Food
        fields = [
            "name",
            "protein",
            "carbs",
            "fat"
        ]