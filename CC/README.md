# CC - Job Match Assistant

This project is a starter scaffold for a job search assistant application. The goal is to help find job postings that match a user profile by at least 75% and automate the application process across supported job sites.

## Project structure

- `main.py` - entrypoint for the assistant.
- `job_assistant.py` - core logic for profile matching, job search, and automated application.
- `requirements.txt` - Python dependencies.

## Getting started

1. Create and activate a Python virtual environment.
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies.
   ```powershell
   pip install -r requirements.txt
   ```
3. Run the CLI assistant.
   ```powershell
   python main.py --profile profile.json
   ```
4. Run the browser UI.
   ```powershell
   python app.py
   ```
   Then open `http://127.0.0.1:5000` in your browser.

## Notes

This scaffold provides the basic structure and placeholder logic. The next steps are:
- define the profile schema
- implement site-specific job search and apply automation
- add secure credential handling and rate limiting
- add logging and retry behavior
