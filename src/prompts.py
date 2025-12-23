"""
Prompt templates used by the Smart Study Buddy app.

These prompts are intentionally strict to:
- Prevent hallucination
- Enforce PDF-only grounding
- Require structured JSON output
- Enable page-based citations
"""

QUIZ_GENERATION_PROMPT = """
You are an AI quiz generator.

IMPORTANT RULES:
- Use ONLY the provided study excerpts.
- Do NOT use outside knowledge.
- If information is missing, do not invent it.
- Every question MUST include a citation.

TASK:
Create {num_questions} multiple-choice questions at {difficulty} difficulty.

Return STRICT JSON in the following format:
{{
  "questions": [
    {{
      "id": "q1",
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer_index": 0,
      "topic": "Short topic label",
      "citations": [
        {{
          "page_start": 3,
          "page_end": 3,
          "supporting_quote": "Short quote from the study excerpt"
        }}
      ]
    }}
  ]
}}

STUDY EXCERPTS:
{context}
"""
