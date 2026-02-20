from django.contrib import admin
from .models import Topic, ConceptTag, Attempt, Turn, NoteUpload


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


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "student_name", "topic", "mode", "status", "turn_count", "created_at"]
    list_filter = ["mode", "status", "topic"]
    search_fields = ["student_name"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [TurnInline]


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
