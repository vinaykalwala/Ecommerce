from django import forms
from .models import InventoryLog

class StockAdjustForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'})
    )
    action = forms.ChoiceField(
        choices=[('add', 'Add Stock'), ('remove', 'Remove Stock')], 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    remarks = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Remarks (optional)'})
    )

class InventoryLogForm(forms.ModelForm):
    class Meta:
        model = InventoryLog
        fields = ['quantity', 'action', 'remarks']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'action': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }