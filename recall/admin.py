from django.contrib import admin
from .models import (
    Topic, ConceptTag, Attempt, Turn, NoteUpload,
    TransferScenario, TransferAttempt, TransferScaffold,
)


class ConceptTagInline(admin.TabularInline):
    model = ConceptTag
    extra = 1


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ["name", "standard", "concept_count"]
    list_filter = ["standard"]
    search_fields = ["name", "standard"]
    inlines = [ConceptTagInline]

    def concept_count(self, obj):
        return len(obj.expected_concepts)
    concept_count.short_description = "# Concepts"


class TurnInline(admin.TabularInline):
    model = Turn
    extra = 0
    readonly_fields = ["turn_number", "prompt", "student_response", "ai_feedback", "is_correct"]


class TransferAttemptInline(admin.TabularInline):
    model = TransferAttempt
    extra = 0
    readonly_fields = [
        "scenario", "student_response", "transfer_outcome",
        "transfer_score", "transfer_failure_type", "scaffold_count", "submitted_at",
    ]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "student_name", "topic", "mode", "status", "turn_count", "current_transfer_level", "created_at"]
    list_filter = ["mode", "status", "topic"]
    search_fields = ["student_name"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [TurnInline, TransferAttemptInline]


@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ["attempt", "turn_number", "is_correct", "created_at"]
    list_filter = ["is_correct"]


@admin.register(NoteUpload)
class NoteUploadAdmin(admin.ModelAdmin):
    list_display = ["attempt", "uploaded_at"]


@admin.register(ConceptTag)
class ConceptTagAdmin(admin.ModelAdmin):
    list_display = ["name", "topic", "is_misconception"]
    list_filter = ["is_misconception", "topic"]


class TransferScaffoldInline(admin.TabularInline):
    model = TransferScaffold
    extra = 0
    readonly_fields = ["scaffold_type", "scaffold_text", "order", "helped"]


@admin.register(TransferScenario)
class TransferScenarioAdmin(admin.ModelAdmin):
    list_display = ["topic", "transfer_level", "domain_context", "is_ai_generated", "created_at"]
    list_filter = ["transfer_level", "topic", "is_ai_generated"]
    search_fields = ["scenario_text", "domain_context"]


@admin.register(TransferAttempt)
class TransferAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "attempt", "scenario", "transfer_outcome", "transfer_score",
        "transfer_failure_type", "scaffold_count", "submitted_at",
    ]
    list_filter = ["transfer_outcome", "transfer_failure_type"]
    readonly_fields = [
        "attempt", "scenario", "student_response", "transfer_outcome",
        "concept_mappings_detected", "reasoning_chain", "transfer_failure_type",
        "transfer_failure_diagnosis", "transfer_score", "scaffold_count", "submitted_at",
    ]
    inlines = [TransferScaffoldInline]


@admin.register(TransferScaffold)
class TransferScaffoldAdmin(admin.ModelAdmin):
    list_display = ["transfer_attempt", "scaffold_type", "order", "helped"]
    list_filter = ["scaffold_type", "helped"]
