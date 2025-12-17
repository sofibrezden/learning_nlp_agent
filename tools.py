import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

TOPIC_BANK = [
    "Tokenization: BPE/WordPiece, OOV, trade-offs",
    "Embeddings: word2vec/GloVe vs contextual (BERT), pros/cons",
    "TF-IDF vs BM25 vs dense retrieval, when to use which",
    "Language modeling: perplexity, n-grams vs neural LMs",
    "Transformers: self-attention, positional encoding, complexity",
    "Fine-tuning vs prompt engineering vs RAG",
    "Evaluation: precision/recall/F1, ROC-AUC, BLEU/ROUGE, pitfalls",
    "NER / POS tagging: sequence labeling, CRF vs transformer heads",
]
DATA_DIR = Path("data")
STUDENTS_PATH = DATA_DIR / "students.json"
SESSIONS_PATH = DATA_DIR / "exam_sessions.jsonl"
RESULTS_PATH = DATA_DIR / "exam_results.jsonl"


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_students() -> List[Dict[str, str]]:
    if not STUDENTS_PATH.exists():
        return []
    raw = STUDENTS_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def find_student_by_email(email: str) -> Optional[Dict[str, str]]:
    students = read_students()
    return next((s for s in students if s["email"].strip().lower() == email.strip().lower()), None)


def append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def start_exam(email: str, name: str) -> Dict[str, Any]:
    email_l = email.strip().lower()
    name_l = name.strip().lower()

    match = find_student_by_email(email_l)

    if not match:
        return {
            "ok": False,
            "error": "student_not_found",
            "message": "Нема такого юзера на потоці.",
        }

    if match.get("name", "").strip().lower() != name_l:
        return {
            "ok": False,
            "error": "name_email_mismatch",
            "message": "Імʼя не збігається з реєстром для цього email.",
        }

    k = random.choice([2, 3])
    topics = random.sample(TOPIC_BANK, k=k)

    st.session_state.exam = {
        "email": match["email"],
        "name": match["name"],
        "topics": topics,
        "idx": 0,
        "started_at": iso_now(),
    }

    append_jsonl(
        SESSIONS_PATH,
        {
            "event": "start_exam",
            "email": match["email"],
            "name": match["name"],
            "topics": topics,
            "ts": iso_now(),
        },
    )

    return {"ok": True, "topics": topics}


def get_next_topic() -> Dict[str, Any]:
    exam = st.session_state.get("exam")
    if not exam:
        return {"ok": False, "error": "exam_not_started", "done": True}

    if exam["idx"] >= len(exam["topics"]):
        return {"ok": True, "done": True, "remaining": 0}

    topic = exam["topics"][exam["idx"]]
    exam["idx"] += 1
    st.session_state.exam = exam
    return {
        "ok": True,
        "done": False,
        "topic": topic,
        "remaining": len(exam["topics"]) - exam["idx"],
    }


def end_exam(
    email: str,
    score: float,
    history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    record = {
        "email": email,
        "name": st.session_state.get("exam", {}).get("name"),
        "score": float(score),
        "started_at": st.session_state.get("exam", {}).get("started_at"),
        "ended_at": iso_now(),
        "history": history,
    }

    append_jsonl(RESULTS_PATH, {"event": "end_exam", **record})
    user_file = export_user_results(record)

    st.session_state.pop("exam", None)
    st.session_state.pop("audit_history", None)

    st.session_state["last_result"] = record
    st.session_state["last_result_blob"] = json.dumps(record, ensure_ascii=False, indent=2)

    return {
        "ok": True,
        "result": record,
        "download_path": str(user_file),
    }


def export_user_results(record: Dict[str, Any]) -> Path:
    results_dir = DATA_DIR / "tmp_results"
    results_dir.mkdir(exist_ok=True)

    for f in results_dir.glob("*.json"):
        try:
            f.unlink()
        except Exception as e:
            print(f"Не вдалося видалити {f}: {e}")

    filename = f"result_{record['email'].replace('@', '_')}_{int(datetime.now().timestamp())}.json"
    path = results_dir / filename

    path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def tool_router(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "start_exam":
        return start_exam(email=args["email"], name=args["name"])
    if name == "get_next_topic":
        return get_next_topic()
    if name == "end_exam":
        return end_exam(email=args["email"], score=args["score"], history=args.get("history"))
    return {"ok": False, "error": f"unknown_tool:{name}"}
