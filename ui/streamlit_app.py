import streamlit as st
import os
import io
import requests
from typing import Optional

# -----------------------------
# Deployment detection
# -----------------------------
DEPLOYED = os.getenv("STREAMLIT_SERVER_HEADLESS") == "true"

# -----------------------------
# Optional dependencies
# -----------------------------
try:
    from streamlit_js_eval import streamlit_js_eval
except ImportError:
    streamlit_js_eval = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

# -----------------------------
# Backend imports (ONLY used when deployed)
# -----------------------------
if DEPLOYED:
    from crew.agents.resume_agent import ResumeAgent
    from crew.agents.job_discovery import JobDiscoveryAgent
    from crew.agents.matcher_agent import MatcherAgent
    from crew.agents.outreach_agent import OutreachAgent
    from crew.agents.tracker_agent import TrackerAgent
    from storage.db import init_db

# -----------------------------
# Constants
# -----------------------------
API_BASE_URL = "http://127.0.0.1:8000"  # Local dev only


# -----------------------------
# Helper Functions
# -----------------------------
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""

    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")

    if uploaded_file.type == "application/pdf" and PdfReader:
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

    st.error("Unsupported file type. Upload TXT or PDF.")
    return ""


def run_pipeline_backend(
    resume_text: str,
    query: str,
    location: Optional[str],
    max_results: int,
    min_score: int,
):
    """
    Local development → call FastAPI backend
    """
    payload = {
        "resume_text": resume_text,
        "query": query,
        "location": location,
        "max_results": max_results,
        "min_score": min_score,
    }

    response = requests.post(
        f"{API_BASE_URL}/run-pipeline",
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def run_pipeline_inline(
    resume_text: str,
    query: str,
    location: Optional[str],
    max_results: int,
    min_score: int,
):
    """
    Streamlit Cloud → run pipeline in-process
    """
    init_db()

    resume_agent = ResumeAgent()
    job_agent = JobDiscoveryAgent()
    matcher_agent = MatcherAgent()
    outreach_agent = OutreachAgent()
    tracker_agent = TrackerAgent()

    resume = resume_agent.parse(resume_text)
    jobs = job_agent.discover(query=query, location=location, max_results=max_results)
    scored = matcher_agent.score(resume, jobs)

    results = []

    for job, score in scored:
        if score < min_score:
            continue

        try:
            message = outreach_agent.generate_message(resume, job, score)
        except Exception:
            message = ""

        try:
            tracker_agent.track(
                job_id=job.job_id,
                job_title=job.title,
                company=job.company,
                fit_score=score,
                outreach_message=message,
            )
        except Exception:
            pass

        results.append(
            {
                "job_id": job.job_id,
                "title": job.title,
                "company": job.company,
                "fit_score": score,
                "outreach_message": message,
                "url": job.url,
            }
        )

    return {"results": results}


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Multi-Agent Job Search", page_icon="🔍", layout="wide")

st.title("🔍 Multi-Agent Job Search System")

st.markdown(
    """
AI-powered job search assistant with transparent reasoning and personalized outreach.

**Note:**  
- Local dev uses a FastAPI backend  
- Deployed version runs the pipeline in-process due to platform constraints
"""
)

# -----------------------------
# Sidebar inputs
# -----------------------------
st.sidebar.header("Search Parameters")

uploaded_file = st.sidebar.file_uploader("Upload Resume (TXT or PDF)", type=["txt", "pdf"])

resume_text = (
    extract_text_from_file(uploaded_file)
    if uploaded_file
    else st.sidebar.text_area("Or paste resume text", height=200)
)

query = st.sidebar.text_input("Job Query", placeholder="e.g. machine learning intern")
location = st.sidebar.text_input("Location (optional)", placeholder="e.g. India")

max_results = st.sidebar.slider("Max Results", 1, 10, 5)
min_score = st.sidebar.slider("Minimum Fit Score", 0, 100, 50)

# -----------------------------
# Run pipeline
# -----------------------------
if st.sidebar.button("🚀 Run Job Search", type="primary"):
    if not resume_text.strip():
        st.error("Please provide resume text.")
    elif not query.strip():
        st.error("Please provide a job query.")
    else:
        with st.spinner("Running job search pipeline..."):
            try:
                if DEPLOYED:
                    result = run_pipeline_inline(
                        resume_text, query, location or None, max_results, min_score
                    )
                else:
                    result = run_pipeline_backend(
                        resume_text, query, location or None, max_results, min_score
                    )
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                result = None

        if result:
            results = result.get("results", [])
            if not results:
                st.warning("No matching jobs found.")
            else:
                st.success(f"Found {len(results)} matching job(s)")
                for i, job in enumerate(results, 1):
                    st.subheader(f"{i}. {job['title']} @ {job['company']}")
                    st.write(f"**Fit Score:** {job['fit_score']}/100")

                    if job.get("url"):
                        st.markdown(f"[Apply here]({job['url']})")

                    st.markdown("**Outreach Message**")
                    st.code(job["outreach_message"])
                    st.divider()

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and FastAPI")
