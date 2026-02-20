"""
AI service layer for the Adaptive Recall Engine.

Wraps OpenAI API calls behind clean functions so views stay thin.
All prompts are carefully tuned for middle-school biology (Georgia Standards).
"""

import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_client():
    """Lazily create an OpenAI client."""
    from openai import OpenAI

    return OpenAI(api_key=settings.OPENAI_API_KEY)


# ─── System prompts ──────────────────────────────────────────────────────────

SYSTEM_BRAIN_DUMP_ANALYSIS = """You are a supportive middle-school biology tutor aligned to the Georgia Standards of Excellence.

A student just did a "brain dump" — they typed everything they remember about the topic "{topic_name}" (standard {standard}).

Your job:
1. Identify which expected concepts the student demonstrated understanding of.
2. Identify which expected concepts are MISSING from their response.
3. Identify any MISCONCEPTIONS (things the student stated incorrectly).
4. For each misconception, write a SHORT, age-appropriate correction (2-3 sentences max).
5. Generate ONE targeted follow-up question that probes the most critical gap.
6. Keep language encouraging, low-stakes, and at a 6th-8th grade reading level.

Expected concepts for this topic:
{expected_concepts}

Common misconceptions to watch for:
{common_misconceptions}

Respond ONLY with valid JSON in this exact structure:
{{
  "demonstrated_concepts": ["concept1", "concept2"],
  "missing_concepts": ["concept3", "concept4"],
  "misconceptions": [
    {{"claim": "what the student said wrong", "correction": "short age-appropriate correction"}}
  ],
  "overall_feedback": "1-2 encouraging sentences about what they got right.",
  "follow_up_question": "One targeted question probing the biggest gap.",
  "is_correct": null
}}
"""

SYSTEM_FOLLOWUP_ANALYSIS = """You are a supportive middle-school biology tutor aligned to the Georgia Standards of Excellence.

The student is working on the topic "{topic_name}" (standard {standard}).

Here is the conversation so far:
{conversation_history}

The student just answered a follow-up question. Evaluate their answer:
1. Is their response correct or mostly correct? (is_correct: true/false)
2. If incorrect, provide a SHORT, encouraging correction (2-3 sentences).
3. Update the lists of demonstrated, missing, and misconceived concepts.
4. If there are still gaps, generate ONE new follow-up question.
5. If the student has shown strong understanding, say so encouragingly.

Expected concepts for this topic:
{expected_concepts}

Respond ONLY with valid JSON in this exact structure:
{{
  "demonstrated_concepts": ["concept1", "concept2"],
  "missing_concepts": ["concept3"],
  "misconceptions": [
    {{"claim": "what was wrong", "correction": "short correction"}}
  ],
  "overall_feedback": "Encouraging feedback about their latest answer.",
  "follow_up_question": "Next probing question, or empty string if mastery is near.",
  "is_correct": true
}}
"""

SYSTEM_NOTES_EXTRACTION = """You are a middle-school biology curriculum specialist aligned to the Georgia Standards of Excellence.

A student uploaded their class notes (text below). Extract the key biology concepts present in the notes.

Topic: "{topic_name}" (standard {standard})

Expected concepts for this topic:
{expected_concepts}

From the student's notes, identify:
1. Which expected concepts are COVERED in the notes.
2. Which expected concepts are MISSING from the notes.
3. Any statements in the notes that reflect MISCONCEPTIONS.

Respond ONLY with valid JSON:
{{
  "covered_concepts": ["concept1", "concept2"],
  "missing_concepts": ["concept3"],
  "misconceptions": [
    {{"claim": "what the notes say wrong", "correction": "short correction"}}
  ]
}}
"""

SYSTEM_QUIZ_GENERATION = """You are a supportive middle-school biology tutor creating a low-stakes quiz.

Topic: "{topic_name}" (standard {standard})

Based on the student's notes analysis:
- Covered concepts: {covered_concepts}
- Missing concepts: {missing_concepts}
- Misconceptions: {misconceptions}

Generate exactly {num_questions} short-answer questions that:
1. Focus on MISSING concepts and MISCONCEPTIONS (prioritize gaps).
2. Use age-appropriate language (grades 6-8).
3. Require conceptual understanding, not just vocabulary recall.
4. Are encouraging and low-stakes in tone.

Respond ONLY with valid JSON:
{{
  "questions": [
    {{
      "question": "The question text",
      "target_concept": "which concept this tests",
      "hint": "A small hint if the student is stuck"
    }}
  ]
}}
"""

SYSTEM_QUIZ_EVALUATION = """You are a supportive middle-school biology tutor evaluating a quiz answer.

Topic: "{topic_name}" (standard {standard})
Question: "{question}"
Target concept: "{target_concept}"
Student's answer: "{student_answer}"

Evaluate the student's answer:
1. Is it correct or mostly correct?
2. If incorrect or incomplete, explain WHY in 2-3 encouraging sentences.
3. Provide the correct/complete answer.

Respond ONLY with valid JSON:
{{
  "is_correct": true,
  "feedback": "Encouraging feedback about their answer.",
  "correct_answer": "The complete correct answer for reference.",
  "concept_demonstrated": true
}}
"""

SYSTEM_SUMMARY = """You are a supportive middle-school biology tutor writing a session summary.

Topic: "{topic_name}" (standard {standard})
Session mode: {mode}
Turns completed: {turn_count}
End reason: {end_reason}

Concepts the student demonstrated: {demonstrated}
Concepts still missing: {missing}
Misconceptions identified: {misconceptions}

Write a brief, encouraging summary (4-6 sentences) that:
1. Celebrates what the student knows well.
2. Gently names 1-2 areas to review.
3. Includes one reflection prompt (e.g., "What surprised you about...?").
4. Uses age-appropriate, non-evaluative language.

Respond ONLY with valid JSON:
{{
  "what_you_know_well": ["concept1", "concept2"],
  "what_to_review_next": ["concept3"],
  "summary_text": "The encouraging summary paragraph.",
  "reflection_prompt": "A thought-provoking reflection question."
}}
"""


# ─── API call helpers ─────────────────────────────────────────────────────────

def _chat(system_prompt: str, user_message: str) -> dict:
    """
    Send a chat completion request and parse the JSON response.
    Returns a dict on success, or a dict with an 'error' key on failure.
    """
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_completion_tokens=1500,
        )
        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1]  # remove first line
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse AI JSON response: %s\nRaw: %s", e, content)
        return {"error": f"Failed to parse AI response: {e}"}
    except Exception as e:
        logger.error("OpenAI API error: %s", e)
        return {"error": f"AI service error: {e}"}


# ─── Public functions used by views ───────────────────────────────────────────

def analyze_brain_dump(topic, student_text: str) -> dict:
    """
    Mode 1, Turn 1: analyze a student's initial brain dump.
    Returns structured feedback dict.
    """
    system = SYSTEM_BRAIN_DUMP_ANALYSIS.format(
        topic_name=topic.name,
        standard=topic.standard,
        expected_concepts=json.dumps(topic.expected_concepts),
        common_misconceptions=json.dumps(topic.common_misconceptions),
    )
    return _chat(system, f"Student's brain dump:\n\n{student_text}")


def analyze_followup(topic, conversation_history: str, student_response: str) -> dict:
    """
    Mode 1, Turn 2+: analyze a student's follow-up answer.
    """
    system = SYSTEM_FOLLOWUP_ANALYSIS.format(
        topic_name=topic.name,
        standard=topic.standard,
        conversation_history=conversation_history,
        expected_concepts=json.dumps(topic.expected_concepts),
    )
    return _chat(system, f"Student's response:\n\n{student_response}")


def extract_notes_concepts(topic, notes_text: str) -> dict:
    """
    Mode 2: extract concepts from uploaded notes.
    """
    system = SYSTEM_NOTES_EXTRACTION.format(
        topic_name=topic.name,
        standard=topic.standard,
        expected_concepts=json.dumps(topic.expected_concepts),
    )
    return _chat(system, f"Student's notes:\n\n{notes_text[:4000]}")  # truncate very long notes


def generate_quiz_questions(topic, covered, missing, misconceptions, num_questions=4) -> dict:
    """
    Mode 2: generate quiz questions based on notes analysis.
    """
    system = SYSTEM_QUIZ_GENERATION.format(
        topic_name=topic.name,
        standard=topic.standard,
        covered_concepts=json.dumps(covered),
        missing_concepts=json.dumps(missing),
        misconceptions=json.dumps(misconceptions),
        num_questions=num_questions,
    )
    return _chat(system, "Generate the quiz questions now.")


def evaluate_quiz_answer(topic, question: str, target_concept: str, student_answer: str) -> dict:
    """
    Mode 2: evaluate a single quiz answer.
    """
    system = SYSTEM_QUIZ_EVALUATION.format(
        topic_name=topic.name,
        standard=topic.standard,
        question=question,
        target_concept=target_concept,
        student_answer=student_answer,
    )
    return _chat(system, "Evaluate the answer.")


def generate_session_summary(attempt) -> dict:
    """
    Generate an end-of-session summary for any mode.
    """
    end_reason_map = {
        "mastery": "Student reached mastery",
        "max_turns": "Maximum turns reached",
        "opted_out": "Student chose to stop",
        "active": "Session still active",
    }
    system = SYSTEM_SUMMARY.format(
        topic_name=attempt.topic.name,
        standard=attempt.topic.standard,
        mode=attempt.get_mode_display(),
        turn_count=attempt.turn_count,
        end_reason=end_reason_map.get(attempt.status, attempt.status),
        demonstrated=json.dumps(attempt.demonstrated_concepts),
        missing=json.dumps(attempt.missing_concepts),
        misconceptions=json.dumps(attempt.identified_misconceptions),
    )
    return _chat(system, "Generate the session summary.")
