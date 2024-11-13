from django import forms
from .models import Question, Tag

class QuestionForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise forms.ValidationError("Content must be at least 10 characters long.")
        return content
