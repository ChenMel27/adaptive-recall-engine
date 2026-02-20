# URL Routes & Views

## Route Map

```mermaid
graph TD
    subgraph "Home & Setup"
        R1["GET /<br/>home()"]
        R2["POST /start/<br/>start_session()"]
    end

    subgraph "Mode 1: Brain Dump"
        R3["GET /brain-dump/:id/<br/>brain_dump()"]
        R4["POST /brain-dump/:id/submit/<br/>brain_dump_submit()"]
    end

    subgraph "Mode 2: Notes Quiz"
        R5["GET /notes/:id/<br/>notes_upload()"]
        R6["POST /notes/:id/submit/<br/>notes_upload_submit()"]
        R7["GET /quiz/:id/<br/>quiz()"]
        R8["POST /quiz/:id/submit/<br/>quiz_submit()"]
    end

    subgraph "Session Controls"
        R9["POST /opt-out/:id/<br/>opt_out()"]
        R10["GET /summary/:id/<br/>summary()"]
    end

    subgraph "Teacher"
        R11["GET /dashboard/<br/>dashboard()"]
    end

    R1 -->|"Choose mode"| R2
    R2 -->|"brain_dump mode"| R3
    R2 -->|"notes_quiz mode"| R5

    R3 --> R4
    R4 -->|"Continue"| R3
    R4 -->|"End"| R10

    R5 --> R6
    R6 --> R7
    R7 --> R8
    R8 -->|"More Qs"| R7
    R8 -->|"Done"| R10

    R3 -.->|"Opt out"| R9
    R7 -.->|"Opt out"| R9
    R9 --> R10

    R10 -->|"New session"| R1
    R10 -->|"Dashboard"| R11

    style R1 fill:#6c5ce7,color:#fff
    style R10 fill:#00b894,color:#fff
    style R11 fill:#fdcb6e,color:#333
```

## View → Template Mapping

```mermaid
graph LR
    subgraph Views["views.py"]
        V1["home()"]
        V2["brain_dump()"]
        V3["notes_upload()"]
        V4["quiz()"]
        V5["summary()"]
        V6["dashboard()"]
    end

    subgraph Templates["templates/recall/"]
        T0["base.html"]
        T1["home.html"]
        T2["brain_dump.html"]
        T3["notes_upload.html"]
        T4["quiz.html"]
        T5["summary.html"]
        T6["dashboard.html"]
    end

    V1 --> T1
    V2 --> T2
    V3 --> T3
    V4 --> T4
    V5 --> T5
    V6 --> T6

    T1 -->|extends| T0
    T2 -->|extends| T0
    T3 -->|extends| T0
    T4 -->|extends| T0
    T5 -->|extends| T0
    T6 -->|extends| T0
```

## HTTP Method Summary

| Route | Method | View | Purpose |
|-------|--------|------|---------|
| `/` | GET | `home()` | Landing page with start form |
| `/start/` | POST | `start_session()` | Create Attempt, redirect to mode |
| `/brain-dump/<id>/` | GET | `brain_dump()` | Show brain dump page |
| `/brain-dump/<id>/submit/` | POST | `brain_dump_submit()` | Process brain dump/follow-up |
| `/notes/<id>/` | GET | `notes_upload()` | Show upload form |
| `/notes/<id>/submit/` | POST | `notes_upload_submit()` | Upload PDF, extract, gen quiz |
| `/quiz/<id>/` | GET | `quiz()` | Show current quiz question |
| `/quiz/<id>/submit/` | POST | `quiz_submit()` | Evaluate answer |
| `/opt-out/<id>/` | POST | `opt_out()` | End session early |
| `/summary/<id>/` | GET | `summary()` | Generate & show summary |
| `/dashboard/` | GET | `dashboard()` | Teacher overview |
