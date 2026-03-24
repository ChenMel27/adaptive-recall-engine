# BioRecall — Adaptive Recall Engine

## What is this?

BioRecall is a web app I built to help middle school biology students (grades 6–8) study smarter. It's aligned to the Georgia Standards of Excellence (S7L1–S7L5) and uses AI to give students real-time feedback on what they know and what they're still working on — without any grades or pressure.

The idea came from research on **active recall** and **metacognition** — basically, students learn better when they practice pulling information from memory instead of just re-reading their notes, and when they become aware of their own knowledge gaps. BioRecall is designed around those principles.

---

## How It Works

There are three study modes. Students pick a biology topic, then choose how they want to practice.

### Mode 1 — Brain Dump
The student types everything they can remember about a topic in their own words. The AI reads their response and figures out which concepts they nailed, which ones they missed, and whether they have any misconceptions. Then it asks a follow-up question targeting their biggest gap. This back-and-forth continues for up to 6 rounds (or until the student reaches mastery or decides to stop).

### Mode 2 — Notes Upload & Quiz
The student uploads a PDF of their class notes. The AI reads through the notes, identifies what's covered and what's missing, and generates a short quiz based on the gaps. Questions are connected to what the student actually wrote, so it feels personalized rather than random. Each answer gets immediate feedback.

### Mode 3 — Transfer Challenge
This one tests whether students can apply what they've learned in a completely new context. The AI generates scenarios in unfamiliar domains (cooking, engineering, space, etc.) and the student has to recognize the underlying biology. There are 4 levels of increasing difficulty, from near transfer to creative problem-solving.

### After Every Session
Students get a summary that breaks down:
- **What they nailed** — concepts they explained well
- **Got it with a nudge** — concepts they got right, but only after a follow-up question
- **What to review next** — gaps that still need work
- A reflection prompt to encourage metacognitive thinking

### Teacher Dashboard
There's also a simple dashboard where teachers can see all student sessions, which topics have been covered, and how students are doing overall.

---

## How Sessions End

| Condition | What happens |
|-----------|-------------|
| Mastery reached | No misconceptions left, 2 or fewer missing concepts, at least 2 correct follow-ups |
| Max rounds hit | Session ends after 6 rounds |
| Student opts out | Student clicks "Stop Here" and gets their summary |

---

## Standards Covered

| Standard | Topic |
|----------|-------|
| S7L1 | Diversity of Living Organisms |
| S7L2 | Cells & Organelles / Levels of Organization |
| S7L3 | Reproduction & Genetics |
| S7L4 | Ecosystems & Interdependence |
| S7L5 | Evolution & Natural Selection |

---

## Built With

- **Python / Django** — handles all the backend logic and page rendering
- **OpenAI API** — powers the AI feedback, question generation, and concept analysis
- **SQLite** — lightweight database (no setup needed)
- **PyPDF2** — extracts text from uploaded PDF notes
- **HTML/CSS** — simple frontend, no JavaScript frameworks

---

## Getting It Running

You'll need **Python 3.12+** installed. If you're not sure, open a terminal and type `python3 --version`.

You'll also need an **OpenAI API key** — you can get one at [platform.openai.com](https://platform.openai.com/).

### Step-by-step setup

```bash
# 1. Clone the repo and go into the folder
git clone <repo-url>
cd adaptive-recall-engine

# 2. (Recommended) Create a virtual environment so packages don't conflict
python3 -m venv venv
source venv/bin/activate

# 3. Install the required packages
pip install -r requirements.txt

# 4. Set up your API key
cp .env.example .env
# Open the .env file and paste your OpenAI API key where it says "your-openai-api-key-here"

# 5. Set up the database
python3 manage.py migrate

# 6. Load the biology topics into the database
python3 manage.py seed_topics

# 7. Start the server
python3 manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser. That's it.

> **Optional:** If you want access to Django's admin panel (to view/edit data directly), run `python3 manage.py createsuperuser` and follow the prompts. Then go to `http://127.0.0.1:8000/admin/`.

---

## Project Structure

Here's a quick overview of what's in each folder:

```
adaptive-recall-engine/
├── config/               # Project settings, URL routing
├── recall/               # Main app — models, views, AI logic, forms
│   ├── models.py         # Database models (topics, attempts, turns, etc.)
│   ├── views.py          # Page logic for all three modes
│   ├── ai_service.py     # All the OpenAI prompts and API calls
│   ├── forms.py          # Form handling
│   └── management/       # Custom commands (like seeding topics)
├── templates/recall/     # HTML pages
├── static/css/           # Stylesheet
├── docs/                 # Architecture diagrams (Mermaid format)
├── requirements.txt      # Python dependencies
└── manage.py             # Django entry point
```

---

## Design Decisions

A few things that shaped how I built this:

- **No grades.** Everything is framed as reflection, not evaluation. The language is intentionally warm and encouraging ("not quite" instead of "wrong").
- **Partial credit isn't free.** If a student says something vaguely correct (like "traits are passed down") but misses the key mechanism (genes), the AI keeps it as a gap and probes further instead of just giving credit.
- **Nudge tracking.** If a student only gets a concept right after a follow-up question, they still get credit — but it shows up in the summary as "needed a nudge" so they know to practice recalling it independently.
- **Questions come from the student's notes.** In Mode 2, quiz questions reference what the student actually wrote in their PDF, so it doesn't feel like a generic worksheet.
- **Students can stop anytime.** Clicking "Stop Here" gives a supportive summary instead of penalizing them.

---

## Configuration

These settings live in `config/settings.py` and control session behavior:

| Setting | Default | What it does |
|---------|---------|-------------|
| `MAX_TURNS` | 6 | How many rounds before a session auto-ends |
| `MASTERY_THRESHOLD_MISSING` | 2 | How many concepts can still be missing and count as mastery |
| `MASTERY_THRESHOLD_MISCONCEPTIONS` | 0 | Max misconceptions allowed for mastery (must be zero) |
| `MASTERY_CORRECT_FOLLOWUPS` | 2 | How many follow-ups the student needs to get right |

---

## Docs

The `docs/` folder has more detailed diagrams if you want to dig into the architecture:

- [Architecture overview](docs/architecture.md)
- [Data models & relationships](docs/data-models.md)
- [User flow diagrams](docs/user-flows.md)
- [AI pipeline & prompts](docs/ai-pipeline.md)
- [URL routes](docs/url-routes.md)

These use [Mermaid](https://mermaid.js.org/) syntax and render directly on GitHub.