# Smart Study Buddy 📚🤖

An AI-powered study assistant that converts PDFs into high-quality MCQ quizzes with scoring, topic-level feedback, and source citations.



## 🚀 What this app does
- Upload a PDF (lecture notes, slides, textbooks)
- Automatically extracts and chunks content
- Generates MCQ quizzes using OpenAI
- Scores answers and highlights weak focus areas
- Provides page-level citations (PDF-only)

## 🧠 Why I built this
Studying from long PDFs is time-consuming and inefficient.  
This tool helps learners **test understanding quickly** and **focus on weak areas** without re-reading everything.


## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **Backend / AI**: OpenAI API
- **Document Processing**: PDF text extraction + chunking
- **Language**: Python
- **Deployment-ready**: Streamlit Cloud

## ⚙️ How to run locally

```bash
git clone https://github.com/RamyaVetukuri/llm-apps.git
cd llm-apps/smart-study-buddy
python -m pip install -r requirements.txt
python -m streamlit run app.py
