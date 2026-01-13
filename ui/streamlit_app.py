import streamlit as st
import requests
from typing import Optional
import io

try:
    from streamlit_js_eval import streamlit_js_eval
except ImportError:
    st.error("streamlit-js-eval is required for link redirection. Install it with: pip install streamlit-js-eval")
    streamlit_js_eval = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    st.error("PyPDF2 is required for PDF uploads. Install it with: pip install PyPDF2")
    PdfReader = None


# -----------------------------
# Constants
# -----------------------------
API_BASE_URL = "http://127.0.0.1:8000"  # Assuming backend runs locally


# -----------------------------
# Helper Functions
# -----------------------------
def extract_text_from_file(uploaded_file):
    """
    Extract text from uploaded file (TXT or PDF).
    """
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.type
    if file_type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    elif file_type == "application/pdf" and PdfReader:
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    else:
        st.error("Unsupported file type. Please upload a TXT or PDF file.")
        return ""


def run_pipeline(resume_text: str, query: str, location: Optional[str], max_results: int, min_score: int):
    """
    Call the FastAPI backend to run the job search pipeline.
    """
    payload = {
        "resume_text": resume_text,
        "query": query,
        "location": location,
        "max_results": max_results,
        "min_score": min_score,
    }
    try:
        # Increased timeout to 120 seconds for LLM processing
        response = requests.post(f"{API_BASE_URL}/run-pipeline", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        st.error("Request timed out. The job search may be taking longer due to high demand. Try again or reduce 'Max Results'.")
        return None
    except requests.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}. Ensure the FastAPI server is running on {API_BASE_URL}.")
        return None


# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="Multi-Agent Job Search", page_icon="🔍", layout="wide")

st.title("🔍 Multi-Agent Job Search System")
st.markdown("""
Welcome to the AI-powered job search assistant! Upload your resume or paste text, specify your search criteria, and let our multi-agent system discover, match, and generate outreach messages for relevant jobs.

**Features:**
- Resume parsing and analysis
- Job discovery via search engines
- Fit scoring with AI
- Personalized outreach message generation
- Application tracking

Ensure the backend server is running before proceeding.
""")

# Sidebar for inputs
st.sidebar.header("Search Parameters")

# Resume input: File uploader or text area
uploaded_file = st.sidebar.file_uploader(
    "Upload Resume (TXT or PDF)",
    type=["txt", "pdf"],
    help="Upload your resume file for automatic text extraction."
)

resume_text = ""
if uploaded_file:
    resume_text = extract_text_from_file(uploaded_file)
    st.sidebar.success("Resume uploaded and processed!")
else:
    resume_text = st.sidebar.text_area(
        "Or Paste Resume Text",
        height=200,
        placeholder="Paste your resume here...",
        help="Enter your full resume text for analysis."
    )

query = st.sidebar.text_input(
    "Job Query",
    placeholder="e.g., machine learning intern",
    help="Keywords for job search."
)

location = st.sidebar.text_input(
    "Location (Optional)",
    placeholder="e.g., India",
    help="City or country for location-based search."
)

max_results = st.sidebar.slider(
    "Max Results",
    min_value=1,
    max_value=10,
    value=5,
    help="Maximum number of jobs to discover."
)

min_score = st.sidebar.slider(
    "Minimum Fit Score",
    min_value=0,
    max_value=100,
    value=50,
    help="Only show jobs with fit score above this threshold."
)

# Run button
if st.sidebar.button("🚀 Run Job Search", type="primary"):
    if not resume_text.strip():
        st.error("Please provide resume text via upload or paste.")
    elif not query.strip():
        st.error("Please provide a job query.")
    else:
        with st.spinner("Running job search pipeline... This may take a moment."):
            result = run_pipeline(resume_text, query, location or None, max_results, min_score)
        
        if result:
            results = result.get("results", [])
            if not results:
                st.warning("No jobs found matching your criteria. Try adjusting the parameters.")
            else:
                st.success(f"Found {len(results)} matching job(s)!")
                
                for i, job in enumerate(results, 1):
                    with st.container():
                        st.subheader(f"{i}. {job['title']} @ {job['company']}")
                        st.write(f"**Fit Score:** {job['fit_score']}/100")
                        if job.get('url'):
                            # Display URL for debugging
                            st.write(f"**Job URL:** {job['url']}")
                            # Fallback: Clickable Markdown link (opens in same tab)
                            st.markdown(f"[Apply for {job['title']}]({job['url']})", unsafe_allow_html=False)
                            # Optional: Button with JS (if installed)
                            if streamlit_js_eval:
                                if st.button(f"Open in New Tab", key=f"apply_{i}"):
                                    streamlit_js_eval(js_expressions=f"window.open('{job['url']}', '_blank')")
                        
                        st.markdown("**Outreach Message:** (Copy and paste as needed)")
                        # Use st.code for easy copying
                        st.code(job['outreach_message'], language=None)
                        st.divider()

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and FastAPI. Ensure API keys are configured for full functionality.")