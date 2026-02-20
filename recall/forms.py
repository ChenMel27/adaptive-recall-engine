"""
Django forms for the Adaptive Recall Engine.
"""

from django import forms
from .models import Topic


class StudentNameForm(forms.Form):
    """Collect student name before starting a session."""

    student_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Enter your first name",
            "autofocus": True,
        }),
    )


class TopicSelectForm(forms.Form):
    """Select a topic to study."""

    topic = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Choose a topic...",
    )


class BrainDumpForm(forms.Form):
    """Mode 1: initial brain dump text area."""

    response = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-textarea",
            "rows": 8,
            "placeholder": "Type everything you remember about this topic... Don't worry about being perfect!",
            "autofocus": True,
        }),
        label="Your Brain Dump",
    )


class FollowUpForm(forms.Form):
    """Mode 1: respond to a follow-up question."""

    response = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-textarea",
            "rows": 5,
            "placeholder": "Type your answer here...",
            "autofocus": True,
        }),
        label="Your Answer",
    )


class NotesUploadForm(forms.Form):
    """Mode 2: upload PDF notes."""

    notes_file = forms.FileField(
        widget=forms.FileInput(attrs={
            "class": "form-file",
            "accept": ".pdf",
        }),
        label="Upload Your Notes (PDF)",
        help_text="Upload a PDF of your class notes for this topic.",
    )


class QuizAnswerForm(forms.Form):
    """Mode 2: answer a quiz question."""

    answer = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-textarea",
            "rows": 4,
            "placeholder": "Type your answer...",
            "autofocus": True,
        }),
        label="Your Answer",
    )
