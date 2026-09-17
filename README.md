# RAG Talent Search Engine

> **Evidence-grounded talent discovery system for semantic candidate retrieval, hybrid ranking, and AI-assisted candidate evaluation.**

[![Live Demo](https://img.shields.io/badge/Live-Demo-FF4B4B?logo=streamlit\&logoColor=white)](https://rag-talent-search-engine.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github\&logoColor=white)](https://github.com/AbdelrhmanAkl/rag-talent-search-engine)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit\&logoColor=white)](https://streamlit.io/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-0467DF)](https://github.com/facebookresearch/faiss)

**Live Demo:** https://rag-talent-search-engine.streamlit.app/
**Repository:** https://github.com/AbdelrhmanAkl/rag-talent-search-engine

---

## Overview

**RAG Talent Search Engine** is an end-to-end **Retrieval-Augmented Generation (RAG)** application for natural-language candidate discovery from resume data.

Instead of depending only on keyword matching, the system combines:

* Semantic resume retrieval
* BGE embeddings
* FAISS vector search
* Explicit technical requirement matching
* Hybrid candidate re-ranking
* Near-duplicate profile detection
* Evidence-grounded Gemini evaluation
* Structured JSON-based evaluation
* Streamlit-based candidate discovery interface

The system is designed as a **human-in-the-loop decision-support tool**. It surfaces relevant candidate evidence, matching requirements, and potential gaps for human review rather than making autonomous hiring decisions.

---

## Live Demo

**Try the application:**

https://rag-talent-search-engine.streamlit.app/

Example query:

```text
Machine Learning Engineer with Python, NLP, deep learning,
and experience building production AI systems.
```

The system processes the request through the complete retrieval and evaluation pipeline:

```text
Natural-Language Query
        ↓
Query Embedding
        ↓
FAISS Semantic Retrieval
        ↓
Candidate Evidence Aggregation
        ↓
Requirement Extraction
        ↓
Hybrid Re-ranking
        ↓
Duplicate Detection
        ↓
Gemini Evaluation
        ↓
Structured Candidate Results
```

---

## Why This Project?

Traditional resume search often relies heavily on exact keywords.

For example, a recruiter searching for:

```text
NLP Engineer with Transformer experience
```

may miss a candidate whose resume describes:

```text
Built text classification systems using BERT-based architectures.
```

A semantic retrieval system can identify the conceptual relationship between these descriptions even when the wording is different.

This project therefore separates the problem into two major stages:

### Retrieval

Find potentially relevant evidence from the resume corpus.

### Evaluation

Use retrieved evidence to generate a structured, evidence-grounded assessment.

This **retrieval-before-generation** architecture reduces the dependency on the LLM as a search engine and keeps candidate evaluation tied to retrieved resume information.

---

# System Architecture

```text
                         USER QUERY
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Query Processing   │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Semantic Retrieval   │
                  │ BGE + FAISS          │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Candidate Evidence   │
                  │ Aggregation           │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Requirement          │
                  │ Extraction           │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Hybrid Re-ranking    │
                  │ 70% Semantic         │
                  │ 30% Requirements     │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Deduplication        │
                  │ Threshold = 0.95     │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Gemini Evaluation    │
                  │ Evidence-Grounded    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Structured Results   │
                  │ Streamlit Interface  │
                  └──────────────────────┘
```

---

# Core Components

## 1. Semantic Resume Retrieval

Resume chunks are embedded using:

```text
BAAI/bge-small-en-v1.5
```

The embeddings have a dimension of:

```text
384
```

The vectors are normalized and indexed using:

```text
FAISS IndexFlatIP
```

This enables similarity-based retrieval using natural-language queries rather than relying exclusively on exact keyword matches.

---

## 2. Candidate Evidence Aggregation

Retrieved resume chunks are grouped by candidate.

Instead of treating every retrieved chunk as an independent result, the pipeline reconstructs candidate-level evidence so that multiple pieces of information from the same resume can contribute to the candidate's relevance.

This creates a transition from:

```text
Retrieved Chunks
       ↓
Candidate-Level Evidence
```

which is important for downstream ranking and LLM evaluation.

---

## 3. Hybrid Candidate Re-ranking

Semantic similarity alone is not always sufficient.

A candidate can be semantically similar to a query while missing an explicitly requested technical skill.

The system therefore combines two signals:

```text
Hybrid Score =
    0.70 × Semantic Score
  + 0.30 × Requirement Coverage
```

### Semantic Score

Measures semantic relevance between the query and candidate evidence.

### Requirement Coverage

Checks whether explicitly extracted technical requirements appear within the candidate's available evidence.

This provides a more controlled ranking layer before candidates reach the generative evaluation stage.

---

## 4. Near-Duplicate Detection

Resume datasets can contain repeated or highly similar profiles.

The system detects near-duplicate candidate profiles using normalized text comparison and `SequenceMatcher`.

Configured threshold:

```text
0.95
```

This helps prevent redundant candidate profiles from occupying multiple positions in the final result set.

---

# Evidence-Grounded Gemini Evaluation

After retrieval and ranking, the highest-ranked candidates can be evaluated using **Google Gemini**.

The evaluator receives candidate information retrieved from the resume corpus and produces structured output rather than an unrestricted natural-language judgment.

Typical evaluation fields include:

* Fit summary
* Supporting evidence
* Matching requirements
* Potential gaps
* Evaluation notes
* Bias-awareness checks

The intended flow is:

```text
Resume Evidence
      ↓
Retrieved Candidate Context
      ↓
Gemini
      ↓
Structured Evaluation
```

The LLM is therefore used as an **evaluation layer after retrieval**, not as the primary candidate search mechanism.

---

# Deterministic Evaluation Cache

Gemini evaluations can be cached using deterministic request keys.

This provides two practical benefits:

* Reduces repeated API calls during development and demonstrations
* Avoids regenerating identical evaluations for identical requests

The cache is separated from the public application artifacts.

---

# Technical Configuration

| Component                  | Configuration            |
| -------------------------- | ------------------------ |
| Candidate profiles         | 220                      |
| Resume chunks              | 1,034                    |
| Embedding model            | `BAAI/bge-small-en-v1.5` |
| Embedding dimension        | 384                      |
| Vector index               | FAISS `IndexFlatIP`      |
| Chunk size                 | 1,000                    |
| Chunk overlap              | 150                      |
| Retrieval candidates       | Configurable             |
| Semantic ranking weight    | 70%                      |
| Requirement ranking weight | 30%                      |
| Deduplication threshold    | 0.95                     |
| LLM                        | Google Gemini            |
| Evaluation format          | Structured JSON          |
| Web interface              | Streamlit                |

---

# Example

### Input

```text
Python developer with NLP, transformers, and deep learning experience.
```

### Processing

```text
Query
  ↓
BGE Embedding
  ↓
FAISS Retrieval
  ↓
Candidate Aggregation
  ↓
Requirement Extraction
  ↓
Hybrid Re-ranking
  ↓
Deduplication
  ↓
Gemini Evaluation
```

### Output

The interface presents candidate-level information including:

```text
Candidate
├── Relevance information
├── Supporting resume evidence
├── Matching requirements
├── Potential gaps
└── Gemini evaluation notes
```

The goal is to make the evidence behind each retrieved candidate visible rather than returning an opaque LLM-generated recommendation.

---

# Project Structure

```text
rag-talent-search-engine/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── artifacts/
│   ├── candidate_profiles.json
│   ├── chunks.json
│   ├── resume_faiss.index
│   └── config.json
│
├── notebooks/
│   └── RAG_Talent_Search_Engine_Development.ipynb
│
├── src/
│   │
│   ├── evaluation/
│   │   └── gemini_evaluator.py
│   │
│   ├── pipeline/
│   │   └── search_pipeline.py
│   │
│   ├── presentation/
│   │   └── formatter.py
│   │
│   ├── ranking/
│   │   ├── deduplicator.py
│   │   └── ranker.py
│   │
│   └── retrieval/
│       └── engine.py
│
├── test_evaluator_context.py
├── test_formatter.py
├── test_gemini_e2e.py
├── test_pipeline.py
├── test_ranking.py
└── test_retrieval.py
```

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/AbdelrhmanAkl/rag-talent-search-engine.git

cd rag-talent-search-engine
```

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Gemini API Configuration

The Gemini evaluation layer requires a valid Google Gemini API key.

## Local Development

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

### Linux / macOS

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

**Never commit API keys or secrets to GitHub.**

---

# Streamlit Deployment

The application is deployed using **Streamlit Community Cloud**.

For deployment:

1. Connect the GitHub repository to Streamlit Community Cloud.
2. Select the `main` branch.
3. Set the application entry point to:

```text
app.py
```

4. Add the Gemini API key through Streamlit Secrets.

Example:

```toml
GEMINI_API_KEY = "YOUR_API_KEY"
```

The API key should be stored in the Streamlit application's secret configuration and **must not be committed to the repository**.

The RAG retrieval artifacts required by the application are included in the repository so that the deployed application can initialize the retrieval pipeline without rebuilding the index at startup.

---

# Running Locally

Start the application with:

```bash
streamlit run app.py
```

Or:

```bash
python -m streamlit run app.py
```

The second form is useful when working inside a Python virtual environment because it explicitly runs Streamlit through the active Python interpreter.

---

# Testing

The project includes focused tests covering the major pipeline components.

### Retrieval

```bash
python test_retrieval.py
```

### Ranking

```bash
python test_ranking.py
```

### Pipeline

```bash
python test_pipeline.py
```

### Formatting

```bash
python test_formatter.py
```

Additional tests cover:

* Gemini evaluation context
* Gemini end-to-end integration
* Candidate ranking
* Deduplication
* Retrieval behavior
* Pipeline integration
* Result formatting

The Gemini end-to-end test requires a valid:

```text
GEMINI_API_KEY
```

---

# Design Principles

## Evidence Over Assumptions

Candidate evaluations should be grounded in information present in the retrieved resume evidence.

## Retrieval Before Generation

The LLM is not used as the primary search engine.

Relevant evidence is retrieved first and then passed to the evaluation layer.

## Hybrid Ranking

Semantic similarity can overlook explicit requirements.

The ranking layer therefore combines:

```text
Semantic Relevance
+
Requirement Coverage
```

## Human-in-the-Loop

The system supports candidate discovery and review.

It is not designed to make autonomous employment decisions.

## Reproducible Retrieval

The deployed application uses precomputed retrieval artifacts so the same indexed resume corpus can be loaded consistently without rebuilding the vector index during every application startup.

---

# Dataset & Artifacts

The project uses a public resume dataset obtained from Kaggle.

The repository contains the precomputed artifacts required for the deployed demonstration, including:

```text
candidate_profiles.json
chunks.json
resume_faiss.index
```

These artifacts allow the Streamlit application to load the candidate corpus and FAISS index directly during deployment.

Dataset usage and redistribution should remain subject to the original dataset's Kaggle license and terms.

---

# Limitations

This project is an AI engineering portfolio demonstration and has several practical limitations.

### Retrieval Quality

Retrieval quality depends on:

* Embedding model performance
* Resume quality
* Chunking strategy
* Query formulation
* Corpus coverage

### Requirement Matching

Requirement coverage currently relies on a controlled technical vocabulary rather than a full skill ontology.

Therefore, synonyms and implicit skills may not always be captured.

### Semantic Retrieval

Semantic retrieval does not guarantee that every relevant candidate will be retrieved.

### LLM Dependency

Gemini evaluation depends on:

* API availability
* API configuration
* Model behavior
* Retrieved context quality

### Resume Quality

Inconsistent resume formatting, incomplete information, or noisy text can affect retrieval and evaluation.

### Human Review

The system is intended for **human-assisted candidate discovery and review**, not automated employment decisions.

---

# Future Improvements

Potential extensions include:

* Cross-encoder re-ranking
* Learned ranking models
* Skill ontology and synonym expansion
* Multilingual retrieval
* Experience-duration extraction
* Structured resume parsing
* Recruiter feedback loops
* Retrieval evaluation datasets
* Recall@K evaluation
* MRR evaluation
* Precision@K evaluation
* Background indexing for larger collections
* Authentication and role-based access control
* Production vector databases for larger-scale deployments
* Monitoring and retrieval observability
* Candidate feedback and search analytics

---

# Tech Stack

### Programming & Application

* Python
* Streamlit

### Retrieval & NLP

* Sentence Transformers
* BGE Embeddings
* FAISS
* Natural Language Processing

### Ranking

* Semantic Similarity
* Requirement Coverage
* Hybrid Scoring
* SequenceMatcher-based Deduplication

### Generative AI

* Google Gemini
* Evidence-grounded evaluation
* Structured JSON generation
* Deterministic evaluation caching

### Engineering

* Git
* GitHub
* Virtual Environments
* Modular Python Architecture
* Automated Caching
* Streamlit Community Cloud

---

# What This Project Demonstrates

This project demonstrates an end-to-end AI engineering workflow covering:

```text
Data
 ↓
Preprocessing
 ↓
Chunking
 ↓
Embedding
 ↓
Vector Indexing
 ↓
Semantic Retrieval
 ↓
Candidate Aggregation
 ↓
Hybrid Ranking
 ↓
Deduplication
 ↓
LLM Evaluation
 ↓
Structured Output
 ↓
Web Deployment
```

Key areas demonstrated:

**RAG · Semantic Search · Vector Databases · NLP · Information Retrieval · Hybrid Ranking · LLM Evaluation · Prompt Engineering · AI Engineering · Streamlit · Deployment**

---

# Portfolio

**RAG Talent Search Engine** was built as a portfolio-grade AI system demonstrating how retrieval, ranking, and generative AI can be combined into a practical end-to-end application.

### Core Engineering Concepts

* Retrieval-Augmented Generation
* Semantic Search
* Vector Search
* FAISS
* Embeddings
* Hybrid Ranking
* Requirement Matching
* Deduplication
* LLM Evaluation
* Evidence Grounding
* Structured Generation
* Caching
* Streamlit Deployment

---

# Links

### Live Application

https://rag-talent-search-engine.streamlit.app/

### GitHub Repository

https://github.com/AbdelrhmanAkl/rag-talent-search-engine

---

# License

No open-source license is currently specified for this repository.

The project is published primarily as a portfolio demonstration.

Dataset usage remains subject to the original dataset's license and terms.


---

# Author

**Abdelrahman Ahmed Akl**

AI Engineer | NLP & RAG | LLMs & Agentic AI

GitHub: https://github.com/AbdelrhmanAkl

---

**Built with Python, FAISS, Sentence Transformers, Google Gemini, and Streamlit.**

