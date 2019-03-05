from django import forms

class InputTextForm(forms.Form):
    input_text = forms.CharField(label='input_text', max_length=100)
