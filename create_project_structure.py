from pathlib import Path

# Use the directory where the script is run as project root
ROOT = Path.cwd()

STRUCTURE = {
    "crew": {
        "__init__.py": None,
        "crew.py": None,
        "agents": {
            "__init__.py": None,
            "job_discovery.py": None,
            "resume_agent.py": None,
            "matcher_agent.py": None,
            "outreach_agent.py": None,
            "tracker_agent.py": None,
        },
    },
    "llm": {
        "__init__.py": None,
        "groq_client.py": None,
        "models.py": None,
        "prompts.py": None,
    },
    "tools": {
        "__init__.py": None,
        "serp_search.py": None,
        "scraper.py": None,
        "embedding.py": None,
    },
    "schemas": {
        "__init__.py": None,
        "job.py": None,
        "resume.py": None,
        "application.py": None,
    },
    "storage": {
        "__init__.py": None,
        "db.py": None,
        "applications.sqlite": None,
    },
    "ui": {
        "__init__.py": None,
        "streamlit_app.py": None,
    },
    "api": {
        "__init__.py": None,
        "main.py": None,
    },
    "config": {
        "__init__.py": None,
        "settings.py": None,
    },
    "main.py": None,
    "requirements.txt": None,
    "README.md": None,
}

def create_structure(base: Path, tree: dict):
    for name, content in tree.items():
        path = base / name

        if content is None:
            path.touch(exist_ok=True)
        else:
            path.mkdir(exist_ok=True)
            create_structure(path, content)

def main():
    print(f"📁 Initializing project structure in: {ROOT}")
    create_structure(ROOT, STRUCTURE)
    print("✅ Project structure created successfully.")

if __name__ == "__main__":
    main()
