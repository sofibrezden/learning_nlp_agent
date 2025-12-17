# AI Examiner Agent — NLP Exam System

An AI-powered examination system for Natural Language Processing (NLP) topics, built with Streamlit and OpenAI. The system conducts interactive exams through a conversational interface, validates students against a registry, and automatically scores and saves exam results.

## Features

- 🤖 **AI-Powered Examiner**: Uses OpenAI's API to conduct intelligent, adaptive exams
- 📝 **Interactive Chat Interface**: Natural conversation-based exam experience
- ✅ **Student Validation**: Verifies students against a registry before starting exams
- 📊 **Topic Management**: Randomly selects 2-3 topics from a predefined bank
- 💾 **Result Tracking**: Automatically saves exam sessions and results to JSON files
- 📥 **Result Export**: Download exam results as JSON files

## Requirements

- Python 3.8 or higher
- OpenAI API key
- Streamlit
- OpenAI Python client

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sofibrezden/learning_nlp_agent.git
cd learning_nlp_agent
```

2. **Install dependencies**:
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your browser to the URL shown in the terminal (typically `http://localhost:8501`)

3. **In the sidebar**:
   - Enter your OpenAI API key (or it will use `OPENAI_API_KEY` from environment)
   - Select your preferred model
   - Click "🔄 Reset session" to start fresh

4. **Taking an exam**:
   - The AI examiner will greet you and ask for your name and email
   - Provide your name and email (must match an entry in `data/students.json`)
   - The system will validate your credentials and start the exam
   - Answer questions about 2-3 randomly selected NLP topics
   - Receive a score (0-10) and feedback at the end
   - Download your results as a JSON file


## Configuration

1. **Student Registry**: Edit `data/students.json` to add or modify student records:
```json
[
  {
    "name": "Student Name",
    "email": "student@example.com"
  }
]
```

2. **OpenAI API Key**: You can set it in two ways:
   - Set environment variable: `export OPENAI_API_KEY="your-api-key"`
   - Enter it in the sidebar when running the app

3. **Model Selection**: The app supports any OpenAI model compatible with your API key (e.g., `gpt-4`, `gpt-4o`, `gpt-3.5-turbo`). Default is `gpt-4.1`.

## Project Structure

```
lab7/
├── app.py              # Main Streamlit application
├── tools.py            # Exam management tools and logic
├── tools.json          # OpenAI function definitions
├── prompt.txt          # System instructions for the AI examiner
├── data/
│   ├── students.json   # Student registry
├── pyproject.toml      # Project configuration and dependencies
└── README.md           # This file
```

## Exam Topics

The system includes a bank of NLP topics:
- Tokenization: BPE/WordPiece, OOV, trade-offs
- Embeddings: word2vec/GloVe vs contextual (BERT), pros/cons
- TF-IDF vs BM25 vs dense retrieval, when to use which
- Language modeling: perplexity, n-grams vs neural LMs
- Transformers: self-attention, positional encoding, complexity
- Fine-tuning vs prompt engineering vs RAG
- Evaluation: precision/recall/F1, ROC-AUC, BLEU/ROUGE, pitfalls
- NER / POS tagging: sequence labeling, CRF vs transformer heads

## How It Works

1. **Student Registration**: The system validates the student's name and email against `data/students.json`
2. **Topic Selection**: Randomly selects 2-3 topics from the topic bank
3. **Interactive Exam**: The AI examiner asks questions and follows up based on responses
4. **Scoring**: The AI evaluates answers and assigns a score (0-10)
5. **Result Storage**: Exam results are saved to individual JSON files per exam

## Notes

- The API key is stored only in the browser session (not persisted)
- Exam history and audit logs are maintained during the session
- Results are automatically saved in JSONL format for easy processing
- The system communicates in Ukrainian by default


## 🌐 Live Demo

You can try the app here:  
👉 [Demo]()

![Demo GIF]()