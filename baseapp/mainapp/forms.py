from django import forms
from .models import Question, Answer


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(max_length=255, required=True,
                           widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}))

    class Meta:
        model = Question
        fields = ['title', 'content']

    def save(self, commit=True):
        question = super().save(commit=False)
        if commit:
            question.save()
        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']