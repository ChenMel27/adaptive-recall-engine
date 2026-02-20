"""
Data models for the Adaptive Recall Engine.

Models
------
Topic           – A biology topic aligned to a Georgia standard (e.g., S7L2).
ConceptTag      – An expected concept within a topic, with optional misconception flag.
Attempt         – One session (Mode 1 or Mode 2) by a student on a topic.
Turn            – A single prompt/response/feedback exchange within an attempt.
NoteUpload      – A PDF upload for Mode 2, with extracted text stored.
"""

import json
from django.db import models
from django.conf import settings as django_settings


# ──────────────────────────────────────────────
# Topic
# ──────────────────────────────────────────────
class Topic(models.Model):
    """A biology topic aligned to Georgia Standards of Excellence."""

    name = models.CharField(max_length=200)
    standard = models.CharField(
        max_length=20,
        help_text="Georgia standard tag, e.g. S7L2",
    )
    description = models.TextField(blank=True)
    expected_concepts = models.JSONField(
        default=list,
        help_text="List of concept strings students should know for this topic.",
    )
    common_misconceptions = models.JSONField(
        default=list,
        help_text="List of known misconceptions for this topic.",
    )

    class Meta:
        ordering = ["standard", "name"]

    def __str__(self):
        return f"[{self.standard}] {self.name}"


# ──────────────────────────────────────────────
# ConceptTag
# ──────────────────────────────────────────────
class ConceptTag(models.Model):
    """
    A single expected concept within a topic.
    Used to track which concepts a student has demonstrated understanding of.
    """

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="concept_tags",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_misconception = models.BooleanField(
        default=False,
        help_text="True if this tag represents a common misconception rather than a correct concept.",
    )

    class Meta:
        ordering = ["topic", "name"]

    def __str__(self):
        prefix = "⚠ " if self.is_misconception else ""
        return f"{prefix}{self.name} ({self.topic.standard})"


# ──────────────────────────────────────────────
# Attempt
# ──────────────────────────────────────────────
class Attempt(models.Model):
    """One learning session by a student on a single topic."""

    MODE_CHOICES = [
        ("brain_dump", "Mode 1 – Word Vomit / Brain Dump"),
        ("notes_quiz", "Mode 2 – Notes Upload & Quiz"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("mastery", "Mastery Reached"),
        ("max_turns", "Max Turns Reached"),
        ("opted_out", "Student Opted Out"),
    ]

    # Simple student_name field keeps the platform low-stakes.
    # Replace with ForeignKey(settings.AUTH_USER_MODEL) for authenticated use.
    student_name = models.CharField(max_length=100, default="Student")
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    turn_count = models.PositiveIntegerField(default=0)
    correct_followups = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Snapshot of analysis state (updated each turn)
    missing_concepts = models.JSONField(default=list)
    identified_misconceptions = models.JSONField(default=list)
    demonstrated_concepts = models.JSONField(default=list)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Attempt #{self.pk} – {self.student_name} – {self.topic.name} ({self.get_mode_display()})"

    # ── business logic ──

    @property
    def max_turns(self):
        return getattr(django_settings, "MAX_TURNS", 6)

    @property
    def mastery_met(self):
        """Check all three mastery sub-conditions."""
        missing_ok = len(self.missing_concepts) <= getattr(
            django_settings, "MASTERY_THRESHOLD_MISSING", 2
        )
        misconceptions_ok = len(self.identified_misconceptions) <= getattr(
            django_settings, "MASTERY_THRESHOLD_MISCONCEPTIONS", 0
        )
        followups_ok = self.correct_followups >= getattr(
            django_settings, "MASTERY_CORRECT_FOLLOWUPS", 2
        )
        return missing_ok and misconceptions_ok and followups_ok

    def check_end_condition(self):
        """
        Evaluate stop rules and update status accordingly.
        Returns the new status string.
        """
        if self.mastery_met:
            self.status = "mastery"
        elif self.turn_count >= self.max_turns:
            self.status = "max_turns"
        # 'opted_out' is set explicitly by the view
        self.save()
        return self.status


# ──────────────────────────────────────────────
# Turn
# ──────────────────────────────────────────────
class Turn(models.Model):
    """A single exchange within an attempt: prompt → student response → AI feedback."""

    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name="turns",
    )
    turn_number = models.PositiveIntegerField()
    prompt = models.TextField(
        help_text="The question or prompt shown to the student.",
    )
    student_response = models.TextField(
        blank=True,
        help_text="What the student typed.",
    )
    ai_feedback = models.JSONField(
        default=dict,
        help_text="Structured AI feedback: missing concepts, misconceptions, explanation, follow-up question.",
    )
    is_correct = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether the student's response was assessed as correct for this follow-up.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["attempt", "turn_number"]
        unique_together = ["attempt", "turn_number"]

    def __str__(self):
        return f"Turn {self.turn_number} of Attempt #{self.attempt_id}"


# ──────────────────────────────────────────────
# NoteUpload (Mode 2)
# ──────────────────────────────────────────────
class NoteUpload(models.Model):
    """A PDF of class notes uploaded by a student for Mode 2."""

    attempt = models.OneToOneField(
        Attempt,
        on_delete=models.CASCADE,
        related_name="note_upload",
    )
    file = models.FileField(upload_to="notes/")
    extracted_text = models.TextField(
        blank=True,
        help_text="Plain text extracted from the PDF.",
    )
    extracted_concepts = models.JSONField(
        default=list,
        help_text="Concepts extracted from the notes by AI.",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notes for Attempt #{self.attempt_id}"
