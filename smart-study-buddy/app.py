import os
import streamlit as st
from dotenv import load_dotenv

from src.pdf_utils import extract_pages
from src.chunking import chunk_pages
from src.quiz_generator import generate_mcq_quiz

load_dotenv()

st.set_page_config(page_title="Smart Study Buddy", layout="wide")
st.title("📚 Smart Study Buddy")
st.caption("Upload a PDF → Generate an MCQ quiz → Score + focus areas with citations (PDF-only).")

# --- Session State ---
if "pages" not in st.session_state:
    st.session_state.pages = None
if "chunks" not in st.session_state:
    st.session_state.chunks = None
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "answers" not in st.session_state:
    st.session_state.answers = {}

# --- Sidebar Settings ---
with st.sidebar:
    st.header("Quiz Settings")
    num_questions = st.number_input("# Questions", min_value=3, max_value=15, value=8)
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)

# --- API Key Check ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning(
        "OPENAI_API_KEY not found. For local runs, create a .env file with OPENAI_API_KEY=... "
        "For Streamlit Cloud, add it in Secrets."
    )

# --- Upload PDF ---
pdf = st.file_uploader("Upload your PDF", type=["pdf"])

col1, col2, col3 = st.columns([1, 1, 1])
process_clicked = col1.button("Process PDF", type="primary")
generate_clicked = col2.button("Generate Quiz")
reset_clicked = col3.button("Reset")

if reset_clicked:
    st.session_state.pages = None
    st.session_state.chunks = None
    st.session_state.quiz = None
    st.session_state.answers = {}
    st.success("Reset complete.")

if pdf and process_clicked:
    pdf_bytes = pdf.read()
    pages = extract_pages(pdf_bytes)
    chunks = chunk_pages(pages)

    st.session_state.pages = pages
    st.session_state.chunks = chunks
    st.session_state.quiz = None
    st.session_state.answers = {}

    st.success(f"Processed {len(pages)} pages into {len(chunks)} text chunks.")

# --- Generate Quiz (LLM) ---
if st.session_state.chunks and generate_clicked:
    with st.spinner("Generating quiz from your PDF..."):
        st.session_state.quiz = generate_mcq_quiz(
            chunks=st.session_state.chunks,
            num_questions=int(num_questions),
            difficulty=difficulty,
        )
        st.session_state.answers = {}
    st.success("Quiz generated!")

# --- Preview (optional) ---
if st.session_state.pages:
    with st.expander("Preview extracted text (first 2 pages)"):
        for p in st.session_state.pages[:2]:
            st.markdown(f"**Page {p['page_num']}**")
            text = (p["text"] or "").strip()
            st.write(text[:1200] + ("..." if len(text) > 1200 else ""))

# --- Render Quiz + Score ---
if st.session_state.quiz:
    st.subheader("Quiz")
    questions = st.session_state.quiz["questions"]

    # 1) FORM: render questions + collect answers (NO scoring here)
    with st.form("quiz_form"):
        for q in questions:
            st.markdown(f"**{q['id']}. {q['question']}**")

            widget_key = f"radio_{q['id']}"
            prev_idx = st.session_state.answers.get(q["id"], None)

            choice = st.radio(
                "Choose one:",
                q["options"],
                index=prev_idx,   # None => no selection
                key=widget_key,
            )

            if choice is None:
                st.session_state.answers[q["id"]] = None
            else:
                st.session_state.answers[q["id"]] = q["options"].index(choice)

        submitted = st.form_submit_button("Submit Quiz")

    # 2) AFTER SUBMIT: validate + score (outside the form)
    if submitted:
        unanswered = [
            q["id"]
            for q in questions
            if st.session_state.answers.get(q["id"]) is None
        ]

        if unanswered:
            st.warning(
                "Please answer all questions before submitting. Unanswered: "
                + ", ".join(unanswered)
            )
            st.stop()

        total = len(questions)
        correct = 0
        missed_topics = {}

        st.subheader("Results")

        for q in questions:
            user_idx = st.session_state.answers.get(q["id"])
            is_correct = (user_idx == q["answer_index"])

            if is_correct:
                correct += 1
            else:
                topic = q.get("topic", "Other")
                missed_topics[topic] = missed_topics.get(topic, 0) + 1

            st.markdown("---")
            st.markdown(f"**{q['id']}. {q['question']}**")
            st.write(f"Your answer: {q['options'][user_idx]}")
            st.write(f"Correct answer: {q['options'][q['answer_index']]}")

            st.write("✅ Correct" if is_correct else "❌ Incorrect")

            st.write("**References (from your PDF):**")
            for c in q.get("citations", []):
                st.write(f"- p{c['page_start']}-{c['page_end']}: “{c['supporting_quote']}”")

        st.markdown("## Score")
        st.write(f"**{correct} / {total}** ({round(correct/total*100)}%)")

        st.markdown("## Focus areas")
        if not missed_topics:
            st.write("Nice — no weak areas detected in this quiz.")
        else:
            for t, n in sorted(missed_topics.items(), key=lambda x: x[1], reverse=True):
                st.write(f"- **{t}** (missed {n} question(s))")

