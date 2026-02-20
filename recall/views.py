"""
Views for the Adaptive Recall Engine.

Flow
----
Home → Choose Mode → (Mode 1 or Mode 2) → Session Loop → Summary

Mode 1 (Brain Dump):
  1. Student picks a topic, types everything they remember.
  2. AI analyses the dump → feedback + follow-up question.
  3. Loop: student answers follow-up → AI re-analyses → repeat.
  4. Ends on mastery / max turns / opt-out → summary page.

Mode 2 (Notes Upload & Quiz):
  1. Student picks a topic, uploads PDF notes.
  2. AI extracts concepts, generates quiz questions.
  3. Student answers each question → immediate feedback.
  4. Ends after all questions answered → summary page.
"""

import json
import logging
from PyPDF2 import PdfReader

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Topic, Attempt, Turn, NoteUpload
from .forms import (
    StudentNameForm,
    TopicSelectForm,
    BrainDumpForm,
    FollowUpForm,
    NotesUploadForm,
    QuizAnswerForm,
)
from . import ai_service

logger = logging.getLogger(__name__)


# ─── Home & Setup ─────────────────────────────────────────────────────────────

def home(request):
    """Landing page with mode selection."""
    topics = Topic.objects.all()
    return render(request, "recall/home.html", {"topics": topics})


def start_session(request):
    """Handle mode + topic selection, create Attempt, redirect to mode view."""
    if request.method != "POST":
        return redirect("recall:home")

    student_name = request.POST.get("student_name", "Student").strip() or "Student"
    topic_id = request.POST.get("topic")
    mode = request.POST.get("mode")  # 'brain_dump' or 'notes_quiz'

    if not topic_id or mode not in ("brain_dump", "notes_quiz"):
        return redirect("recall:home")

    topic = get_object_or_404(Topic, pk=topic_id)

    attempt = Attempt.objects.create(
        student_name=student_name,
        topic=topic,
        mode=mode,
        missing_concepts=topic.expected_concepts,  # start with all missing
    )
    request.session["attempt_id"] = attempt.pk

    if mode == "brain_dump":
        return redirect("recall:brain_dump", attempt_id=attempt.pk)
    else:
        return redirect("recall:notes_upload", attempt_id=attempt.pk)


# ─── Mode 1: Brain Dump ──────────────────────────────────────────────────────

def brain_dump(request, attempt_id):
    """Show the brain dump textarea (turn 1) or the follow-up loop (turn 2+)."""
    attempt = get_object_or_404(Attempt, pk=attempt_id, mode="brain_dump")

    if attempt.status != "active":
        return redirect("recall:summary", attempt_id=attempt.pk)

    turns = attempt.turns.all()
    form = BrainDumpForm() if not turns.exists() else FollowUpForm()

    # Get the last turn's follow-up question if it exists
    last_turn = turns.last()
    follow_up_question = None
    last_feedback = None
    if last_turn and last_turn.ai_feedback:
        follow_up_question = last_turn.ai_feedback.get("follow_up_question", "")
        last_feedback = last_turn.ai_feedback

    context = {
        "attempt": attempt,
        "turns": turns,
        "form": form,
        "follow_up_question": follow_up_question,
        "last_feedback": last_feedback,
        "is_first_turn": not turns.exists(),
    }
    return render(request, "recall/brain_dump.html", context)


@require_POST
def brain_dump_submit(request, attempt_id):
    """Process a brain dump or follow-up response."""
    attempt = get_object_or_404(Attempt, pk=attempt_id, mode="brain_dump")

    if attempt.status != "active":
        return redirect("recall:summary", attempt_id=attempt.pk)

    student_response = request.POST.get("response", "").strip()
    if not student_response:
        return redirect("recall:brain_dump", attempt_id=attempt.pk)

    topic = attempt.topic
    turns = attempt.turns.all()
    turn_number = turns.count() + 1

    if turn_number == 1:
        # First turn: analyse the brain dump
        prompt_text = f"Write everything you remember about: {topic.name}"
        feedback = ai_service.analyze_brain_dump(topic, student_response)
    else:
        # Follow-up turns: build conversation history
        history_parts = []
        for t in turns:
            history_parts.append(f"Prompt: {t.prompt}")
            history_parts.append(f"Student: {t.student_response}")
            if t.ai_feedback.get("overall_feedback"):
                history_parts.append(f"Feedback: {t.ai_feedback['overall_feedback']}")
        conversation_history = "\n".join(history_parts)

        last_turn = turns.last()
        prompt_text = last_turn.ai_feedback.get("follow_up_question", "Follow-up question")
        feedback = ai_service.analyze_followup(topic, conversation_history, student_response)

    # Handle AI errors gracefully
    if "error" in feedback:
        logger.error("AI error in brain dump: %s", feedback["error"])
        feedback = {
            "demonstrated_concepts": attempt.demonstrated_concepts,
            "missing_concepts": attempt.missing_concepts,
            "misconceptions": [],
            "overall_feedback": "I had trouble analyzing your response. Let's try another question!",
            "follow_up_question": f"Can you tell me more about what you know about {topic.name}?",
            "is_correct": None,
        }

    # Create the turn record
    is_correct = feedback.get("is_correct")
    turn = Turn.objects.create(
        attempt=attempt,
        turn_number=turn_number,
        prompt=prompt_text,
        student_response=student_response,
        ai_feedback=feedback,
        is_correct=is_correct,
    )

    # Update attempt state
    attempt.demonstrated_concepts = feedback.get("demonstrated_concepts", [])
    attempt.missing_concepts = feedback.get("missing_concepts", [])
    attempt.identified_misconceptions = [
        m.get("claim", str(m)) for m in feedback.get("misconceptions", [])
    ]
    attempt.turn_count = turn_number
    if is_correct is True:
        attempt.correct_followups += 1

    # Check end conditions
    attempt.check_end_condition()

    if attempt.status != "active":
        return redirect("recall:summary", attempt_id=attempt.pk)

    return redirect("recall:brain_dump", attempt_id=attempt.pk)


# ─── Mode 2: Notes Upload & Quiz ─────────────────────────────────────────────

def notes_upload(request, attempt_id):
    """Show the PDF upload form for Mode 2."""
    attempt = get_object_or_404(Attempt, pk=attempt_id, mode="notes_quiz")

    if hasattr(attempt, "note_upload"):
        return redirect("recall:quiz", attempt_id=attempt.pk)

    form = NotesUploadForm()
    return render(request, "recall/notes_upload.html", {
        "attempt": attempt,
        "form": form,
    })


@require_POST
def notes_upload_submit(request, attempt_id):
    """Process uploaded PDF, extract text, analyse concepts, generate quiz."""
    attempt = get_object_or_404(Attempt, pk=attempt_id, mode="notes_quiz")
    form = NotesUploadForm(request.POST, request.FILES)

    if not form.is_valid():
        return render(request, "recall/notes_upload.html", {
            "attempt": attempt,
            "form": form,
        })

    pdf_file = form.cleaned_data["notes_file"]

    # Extract text from PDF
    try:
        reader = PdfReader(pdf_file)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        extracted_text = "\n".join(text_parts)
    except Exception as e:
        logger.error("PDF extraction error: %s", e)
        form.add_error("notes_file", "Could not read this PDF. Please try a different file.")
        return render(request, "recall/notes_upload.html", {
            "attempt": attempt,
            "form": form,
        })

    if not extracted_text.strip():
        form.add_error("notes_file", "No text found in this PDF. Please upload a text-based PDF (not a scanned image).")
        return render(request, "recall/notes_upload.html", {
            "attempt": attempt,
            "form": form,
        })

    # AI: extract concepts from notes
    topic = attempt.topic
    analysis = ai_service.extract_notes_concepts(topic, extracted_text)

    if "error" in analysis:
        covered = []
        missing = topic.expected_concepts
        misconceptions = []
    else:
        covered = analysis.get("covered_concepts", [])
        missing = analysis.get("missing_concepts", [])
        misconceptions = analysis.get("misconceptions", [])

    # Save the upload
    note_upload = NoteUpload.objects.create(
        attempt=attempt,
        file=pdf_file,
        extracted_text=extracted_text,
        extracted_concepts=covered,
    )

    # AI: generate quiz questions
    num_questions = min(max(len(missing) + len(misconceptions), 3), 6)
    quiz_data = ai_service.generate_quiz_questions(
        topic, covered, missing, misconceptions, num_questions
    )

    if "error" in quiz_data:
        questions = [{"question": f"Explain what you know about {topic.name}.", "target_concept": topic.name, "hint": "Think about the main ideas."}]
    else:
        questions = quiz_data.get("questions", [])

    # Store quiz questions in session
    request.session[f"quiz_{attempt.pk}"] = {
        "questions": questions,
        "current_index": 0,
        "covered_concepts": covered,
        "missing_concepts": missing,
        "misconceptions": misconceptions,
    }

    # Update attempt
    attempt.demonstrated_concepts = covered
    attempt.missing_concepts = missing
    attempt.identified_misconceptions = [m.get("claim", str(m)) for m in misconceptions]
    attempt.save()

    return redirect("recall:quiz", attempt_id=attempt.pk)


def quiz(request, attempt_id):
    """Show the current quiz question for Mode 2."""
    attempt = get_object_or_404(Attempt, pk=attempt_id, mode="notes_quiz")

    if attempt.status != "active":
        return redirect("recall:summary", attempt_id=attempt.pk)

    quiz_state = request.session.get(f"quiz_{attempt.pk}")
    if not quiz_state:
        return redirect("recall:notes_upload", attempt_id=attempt.pk)

    questions = quiz_state["questions"]
    current_index = quiz_state["current_index"]

    if current_index >= len(questions):
        # All questions answered
        attempt.status = "mastery" if attempt.mastery_met else "max_turns"
        attempt.save()
        return redirect("recall:summary", attempt_id=attempt.pk)

    current_question = questions[current_index]
    form = QuizAnswerForm()

    # Get previous turn feedback if any
    last_turn = attempt.turns.last()
    last_feedback = last_turn.ai_feedback if last_turn else None

    context = {
        "attempt": attempt,
        "question": current_question,
        "question_number": current_index + 1,
        "total_questions": len(questions),
        "form": form,
        "last_feedback": last_feedback,
    }
    return render(request, "recall/quiz.html", context)


@require_POST
def quiz_submit(request, attempt_id):
    """Process a quiz answer."""
    attempt = get_object_or_404(Attempt, pk=attempt_id, mode="notes_quiz")

    if attempt.status != "active":
        return redirect("recall:summary", attempt_id=attempt.pk)

    quiz_state = request.session.get(f"quiz_{attempt.pk}")
    if not quiz_state:
        return redirect("recall:notes_upload", attempt_id=attempt.pk)

    student_answer = request.POST.get("answer", "").strip()
    if not student_answer:
        return redirect("recall:quiz", attempt_id=attempt.pk)

    questions = quiz_state["questions"]
    current_index = quiz_state["current_index"]
    current_question = questions[current_index]

    topic = attempt.topic
    turn_number = attempt.turn_count + 1

    # Evaluate the answer
    feedback = ai_service.evaluate_quiz_answer(
        topic,
        current_question["question"],
        current_question.get("target_concept", ""),
        student_answer,
    )

    if "error" in feedback:
        feedback = {
            "is_correct": None,
            "feedback": "I had trouble evaluating your answer. Let's move on!",
            "correct_answer": "",
            "concept_demonstrated": False,
        }

    is_correct = feedback.get("is_correct", False)

    # Create turn record
    Turn.objects.create(
        attempt=attempt,
        turn_number=turn_number,
        prompt=current_question["question"],
        student_response=student_answer,
        ai_feedback=feedback,
        is_correct=is_correct,
    )

    # Update attempt
    attempt.turn_count = turn_number
    if is_correct:
        attempt.correct_followups += 1
        # Add to demonstrated if concept was actually demonstrated
        concept = current_question.get("target_concept", "")
        if concept and concept not in attempt.demonstrated_concepts:
            demonstrated = list(attempt.demonstrated_concepts)
            demonstrated.append(concept)
            attempt.demonstrated_concepts = demonstrated
        # Remove from missing
        missing = list(attempt.missing_concepts)
        if concept in missing:
            missing.remove(concept)
            attempt.missing_concepts = missing

    attempt.save()

    # Advance to next question
    quiz_state["current_index"] = current_index + 1
    request.session[f"quiz_{attempt.pk}"] = quiz_state
    request.session.modified = True

    return redirect("recall:quiz", attempt_id=attempt.pk)


# ─── Opt-Out & Summary ───────────────────────────────────────────────────────

@require_POST
def opt_out(request, attempt_id):
    """Student clicks 'Stop here' — end session early."""
    attempt = get_object_or_404(Attempt, pk=attempt_id)
    if attempt.status == "active":
        attempt.status = "opted_out"
        attempt.save()
    return redirect("recall:summary", attempt_id=attempt.pk)


def summary(request, attempt_id):
    """Show the end-of-session summary page."""
    attempt = get_object_or_404(Attempt, pk=attempt_id)

    # Ensure session is ended
    if attempt.status == "active":
        attempt.check_end_condition()

    turns = attempt.turns.all()

    # Generate AI summary
    ai_summary = ai_service.generate_session_summary(attempt)
    if "error" in ai_summary:
        ai_summary = {
            "what_you_know_well": attempt.demonstrated_concepts,
            "what_to_review_next": attempt.missing_concepts,
            "summary_text": "Great job working through this session! Review the concepts listed below to strengthen your understanding.",
            "reflection_prompt": f"What was the most interesting thing you learned about {attempt.topic.name}?",
        }

    status_messages = {
        "mastery": "🎉 Amazing! You've demonstrated strong understanding of this topic!",
        "max_turns": "Great effort! You've completed all the rounds for this session.",
        "opted_out": "Good job knowing when to take a break! Here's what you covered.",
        "active": "Session in progress...",
    }

    context = {
        "attempt": attempt,
        "turns": turns,
        "ai_summary": ai_summary,
        "status_message": status_messages.get(attempt.status, ""),
    }
    return render(request, "recall/summary.html", context)


# ─── Teacher Dashboard (Optional) ────────────────────────────────────────────

def dashboard(request):
    """Simple teacher dashboard showing all attempts."""
    attempts = Attempt.objects.select_related("topic").order_by("-created_at")[:50]
    topics = Topic.objects.all()

    context = {
        "attempts": attempts,
        "topics": topics,
        "total_attempts": Attempt.objects.count(),
        "mastery_count": Attempt.objects.filter(status="mastery").count(),
    }
    return render(request, "recall/dashboard.html", context)
