import json
from typing import Dict, Any, List

from openai import OpenAI

from src.prompts import QUIZ_GENERATION_PROMPT


def _build_context(chunks: List[dict], max_chars: int = 9000) -> str:
    """
    Build a context string from chunks, including page markers so the model can cite.
    """
    parts = []
    used = 0
    for c in chunks:
        text = (c.get("text") or "").replace("\n", " ").strip()
        if not text:
            continue

        snippet = text[:900]
        block = f"[p{c['page_start']}-{c['page_end']}] {snippet}"
        if used + len(block) > max_chars:
            break

        parts.append(block)
        used += len(block)

    return "\n".join(parts)


def generate_mcq_quiz(
    chunks: List[dict],
    num_questions: int = 8,
    difficulty: str = "medium",
    model: str = "gpt-4.1-mini",
) -> Dict[str, Any]:
    """
    Generates an MCQ quiz strictly grounded in the provided PDF chunks.
    Returns parsed JSON: {"questions": [...]}
    """
    context = _build_context(chunks)

    prompt = QUIZ_GENERATION_PROMPT.format(
        num_questions=num_questions,
        difficulty=difficulty,
        context=context,
    )

    client = OpenAI()

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    raw = resp.choices[0].message.content
    data = json.loads(raw)

    # Minimal validation / guardrails
    if "questions" not in data or not isinstance(data["questions"], list):
        raise ValueError("Model output JSON missing 'questions' list.")

    return data
