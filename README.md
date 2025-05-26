# DocuLearn

**Interactive Learning from Documents**

![DocuLearn Demo](https://github.com/yourusername/DocuLearn/assets/demo.gif)

> Transform static PDFs, slides, and text into quizzes, mind maps, flashcards, and adaptive exercises — powered by AI.

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Architecture](#architecture)
4. [Core Components](#core-components)
5. [Workflow](#workflow)
6. [LLM Integration](#llm-integration)
7. [Example Use Case](#example-use-case)
8. [Technology Stack](#technology-stack)
9. [Future Extensions](#future-extensions)
10. [License](#license)

---

## Overview

DocuLearn takes educational documents (PDFs, PPTs, or plain text) and turns them into personalized, dynamic learning experiences. With the help of Large Language Models (LLMs), the app generates:

- ✅ **Quizzes** (MCQ, True/False, Fill-in-the-blank)
- 🧠 **Mind Maps** (concept visualization)
- 🔁 **Spaced Repetition Flashcards**
- ✨ **Summaries** (key concept extraction)

The content adapts to the user’s learning style and pace.

---

## Goals

- **Automated Content Transformation**: From passive reading to active learning.
- **Adaptive Learning**: Tailored difficulty based on user performance.
- **Cross-Platform Support**: Web, Android, iOS.
- **Gamification**: Badges, leaderboards, and progress tracking.

---

## Architecture

```mermaid
graph LR
  UI["Mobile/Web UI"] --> Parser["Document Parser"]
  Parser --> Analyzer["Content Analyzer"]
  Analyzer --> LLM["LLM Generator"]
  LLM --> QuizEngine["Quiz Engine"]
  LLM --> MindMap["Mind Map Generator"]
  LLM --> Summary["Summary Generator"]
  QuizEngine --> DB[(Database)]
  MindMap --> DB
  Summary --> DB
  Orchestrator["Learning Orchestrator"] --> DB
  Orchestrator --> SRS["Spaced Repetition"]
  Orchestrator --> Progress["Progress Tracker"]
  SRS --> UI
  Progress --> UI
  UI --> Actions["User Actions"]
  Actions --> Analytics["Analytics Engine"]
  Analytics --> DB
