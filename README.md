# 🧬 BioRecall — Adaptive Recall Engine

A **low-stakes metacognitive biology learning platform** for middle school students (Grades 6–8), aligned to the **Georgia Standards of Excellence** (S7L1–S7L5).

Instead of graded quizzes, BioRecall uses two interactive modes to help students discover what they know, identify gaps, and strengthen understanding through guided active recall.

---

## Features

### Mode 1 — Brain Dump ("Word Vomit")
1. Student picks a topic and types **everything they remember**.
2. AI analyzes the response for **demonstrated concepts**, **missing concepts**, and **misconceptions**.
3. The system generates **targeted follow-up questions** that probe the biggest gaps.
4. Loop continues until: **mastery threshold met**, **max turns reached (6)**, or **student opts out**.
5. Session ends with an encouraging **summary + reflection prompt**.

### Mode 2 — Notes Upload & Quiz
1. Student uploads a **PDF of class notes**.
2. AI extracts concepts and generates a **personalized short-answer quiz** focused on gaps.
3. Each answer gets **immediate formative feedback** — no grades, no pressure.
4. Summary highlights strengths and areas to review.

### End Condition Logic
| Rule | Condition |
|------|-----------|
| **Mastery** | 0 misconceptions remaining AND ≤ 2 missing concepts AND ≥ 2 correct follow-ups |
| **Hard Cap** | Turn count ≥ 6 |
| **Opt-Out** | Student clicks "Stop Here" → gets summary of strengths, gaps, and a reflection prompt |

### Teacher Dashboard
View all student sessions, status, and topic coverage at a glance.

---

## Standards Alignment

| Standard | Topic |
|----------|-------|
| S7L1 | Diversity of Living Organisms |
| S7L2 | Cells & Organelles / Levels of Organization |
| S7L3 | Reproduction & Genetics |
| S7L4 | Ecosystems & Interdependence |
| S7L5 | Evolution & Natural Selection |

---

## Tech Stack

- **Backend**: Django 5.1 (Python 3.12)
- **AI**: OpenAI GPT-4o-mini (via `openai` SDK)
- **Database**: SQLite (development)
- **PDF Parsing**: PyPDF2
- **Frontend**: Django templates + custom CSS (no JavaScript frameworks)

---

## Project Structure

```
adaptive-recall-engine/
├── config/               # Django project settings & root URL config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── recall/               # Main application
│   ├── models.py         # Topic, ConceptTag, Attempt, Turn, NoteUpload
│   ├── views.py          # All view logic for both modes
│   ├── ai_service.py     # OpenAI API wrapper + prompt engineering
│   ├── forms.py          # Django forms
│   ├── urls.py           # App URL routing
│   ├── admin.py          # Django admin configuration
│   └── management/
│       └── commands/
│           └── seed_topics.py  # Seed 6 biology topics (S7L1–S7L5)
├── templates/recall/     # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── brain_dump.html
│   ├── notes_upload.html
│   ├── quiz.html
│   ├── summary.html
│   └── dashboard.html
├── static/css/style.css  # Full stylesheet
├── requirements.txt
├── .env.example
└── manage.py
```

---

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd adaptive-recall-engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# 4. Run migrations
python manage.py migrate

# 5. Seed biology topics
python manage.py seed_topics

# 6. (Optional) Create a superuser for the admin panel
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser.

---

## Configuration

Settings in `config/settings.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_TURNS` | 6 | Maximum turns per session |
| `MASTERY_THRESHOLD_MISSING` | 2 | Max missing concepts for mastery |
| `MASTERY_THRESHOLD_MISCONCEPTIONS` | 0 | Max misconceptions for mastery |
| `MASTERY_CORRECT_FOLLOWUPS` | 2 | Correct follow-ups needed for mastery |

---

## Design Principles

- **Low-stakes**: No grades, no penalties — learning-focused feedback only
- **Active recall**: Students retrieve information from memory, not re-read notes
- **Metacognitive**: Students become aware of what they know and don't know
- **Adaptive**: Questions target individual gaps, not one-size-fits-all
- **Student-controlled**: Opt-out at any time with a supportive summary
- **Age-appropriate**: Language and tone designed for grades 6–8