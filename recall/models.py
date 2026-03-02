"""
Data models for the Adaptive Recall Engine.

Models
------
Topic              – A biology topic aligned to a Georgia standard (e.g., S7L2).
ConceptTag         – An expected concept within a topic, with optional misconception flag.
Attempt            – One session (Mode 1, 2, or 3) by a student on a topic.
Turn               – A single prompt/response/feedback exchange within an attempt.
NoteUpload         – A PDF upload for Mode 2, with extracted text stored.
TransferScenario   – A novel-context scenario generated for transfer testing (Mode 3).
TransferAttempt    – A student's response to a transfer scenario, with AI diagnosis.
TransferScaffold   – A progressive hint given during a transfer challenge.
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
        ("transfer", "Mode 3 – Transfer Challenge"),
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

    # Transfer mode tracking
    current_transfer_level = models.PositiveIntegerField(
        default=1,
        help_text="Current transfer level (1-4) for Mode 3.",
    )

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


# ──────────────────────────────────────────────
# TransferScenario (Mode 3)
# ──────────────────────────────────────────────
class TransferScenario(models.Model):
    """A novel-context scenario generated by AI for testing far transfer."""

    TRANSFER_LEVELS = [
        (1, "Near Transfer"),
        (2, "Moderate Transfer"),
        (3, "Far Transfer"),
        (4, "Creative Transfer"),
    ]

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="transfer_scenarios",
    )
    transfer_level = models.IntegerField(
        choices=TRANSFER_LEVELS,
        help_text="1=Near, 2=Moderate, 3=Far, 4=Creative",
    )
    scenario_text = models.TextField(
        help_text="The novel context prompt — deliberately avoids domain jargon.",
    )
    domain_context = models.CharField(
        max_length=100,
        help_text="The novel domain: e.g. 'cooking', 'engineering', 'space exploration'.",
    )
    target_concepts = models.JSONField(
        default=list,
        help_text="Which expected concepts this scenario tests transfer of.",
    )
    expected_mappings = models.JSONField(
        default=list,
        help_text="Concept-to-context mappings the AI expects a successful transfer to include.",
    )
    surface_distractors = models.JSONField(
        default=list,
        help_text="Surface features a student might fixate on that are irrelevant.",
    )
    is_ai_generated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["transfer_level"]

    def __str__(self):
        return f"L{self.transfer_level} Transfer: {self.topic.name} → {self.domain_context}"


# ──────────────────────────────────────────────
# TransferAttempt (Mode 3)
# ──────────────────────────────────────────────
class TransferAttempt(models.Model):
    """A student's response to a transfer scenario, with AI-generated diagnosis."""

    TRANSFER_OUTCOMES = [
        ("no_transfer", "No Transfer — restated definition or guessed"),
        ("surface", "Surface Transfer — used keywords but wrong mapping"),
        ("partial", "Partial Transfer — correct mapping, incomplete reasoning"),
        ("structural", "Structural Transfer — mapped deep structure correctly"),
        ("creative", "Creative Transfer — novel insight beyond expected mappings"),
    ]

    FAILURE_TYPES = [
        ("none", "No failure"),
        ("fixation", "Fixation — stuck on surface features"),
        ("encapsulation", "Encapsulation — can't see concept outside original context"),
        ("overgeneralization", "Overgeneralization — applied concept incorrectly"),
        ("fragmentation", "Fragmentation — mapped some pieces but couldn't integrate"),
        ("inert_knowledge", "Inert Knowledge — knows it but didn't activate it"),
    ]

    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name="transfer_attempts",
    )
    scenario = models.ForeignKey(
        TransferScenario,
        on_delete=models.CASCADE,
        related_name="student_attempts",
    )
    student_response = models.TextField()

    # AI diagnosis fields
    transfer_outcome = models.CharField(
        max_length=20,
        choices=TRANSFER_OUTCOMES,
        default="no_transfer",
    )
    concept_mappings_detected = models.JSONField(
        default=list,
        help_text="Which concept→context mappings the student made.",
    )
    reasoning_chain = models.JSONField(
        default=list,
        help_text="AI's step-by-step analysis of the student's transfer reasoning.",
    )
    transfer_failure_type = models.CharField(
        max_length=25,
        choices=FAILURE_TYPES,
        default="none",
    )
    transfer_failure_diagnosis = models.TextField(
        blank=True,
        help_text="Human-readable explanation of why transfer failed.",
    )
    transfer_score = models.FloatField(
        default=0.0,
        help_text="0.0 to 1.0 score for this transfer attempt.",
    )

    # Scaffolding
    scaffold_count = models.IntegerField(default=0)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return (
            f"Transfer Attempt: {self.attempt.student_name} "
            f"→ L{self.scenario.transfer_level} ({self.transfer_outcome})"
        )

    def weighted_score(self):
        """Higher transfer levels are worth more."""
        return self.transfer_score * self.scenario.transfer_level


# ──────────────────────────────────────────────
# TransferScaffold (Mode 3)
# ──────────────────────────────────────────────
class TransferScaffold(models.Model):
    """A progressive hint that bridges toward transfer without giving the answer."""

    SCAFFOLD_TYPES = [
        ("analogy_prompt", "Analogy Prompt"),
        ("structure_hint", "Structure Hint"),
        ("constraint_removal", "Constraint Removal"),
        ("bridging_context", "Bridging Context"),
        ("explicit_mapping", "Explicit Mapping"),
    ]

    transfer_attempt = models.ForeignKey(
        TransferAttempt,
        on_delete=models.CASCADE,
        related_name="scaffolds",
    )
    scaffold_type = models.CharField(max_length=30, choices=SCAFFOLD_TYPES)
    scaffold_text = models.TextField()
    order = models.IntegerField()
    student_response_after = models.TextField(
        blank=True,
        help_text="What the student wrote after receiving this scaffold.",
    )
    helped = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did transfer improve after this scaffold?",
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Scaffold #{self.order} ({self.scaffold_type}) for TransferAttempt #{self.transfer_attempt_id}"
