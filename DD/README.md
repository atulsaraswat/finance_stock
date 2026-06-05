# DD Job Agent

This project contains a simple AI-style job search and application agent.

The agent loads a user profile and a list of job postings, scores each job for fit, and applies to jobs that match at or above a configured threshold.

## Files

- `main.py` - entry point for running the agent
- `job_agent.py` - agent implementation with job matching, resume generation, and job loading logic
- `profile.json` - sample user profile
- `jobs_sample.json` - sample job postings
- `requirements.txt` - Python dependencies
- `.gitignore` - ignores generated application files

## Usage

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Run the agent and auto-apply to jobs with 75%+ match:

```bash
python c:\AA\DD\main.py --threshold 0.75
```

This displays full details for each job you're applying to.

3. **View all jobs with match scores:**

```bash
python c:\AA\DD\main.py --show-all --min-score 0.5
```

4. **Show top N matching jobs with full details:**

```bash
python c:\AA\DD\main.py --show-all --min-score 0.65 --top 3
```

Displays table of matching jobs, then comprehensive details for top 3.

5. **View specific job details by index:**

```bash
python c:\AA\DD\main.py --view-job 0
python c:\AA\DD\main.py --view-job 1
```

View full details for best, 2nd-best, etc. matching job (0-indexed).

6. **Broader location search with multi-source loading:**

```bash
python c:\AA\DD\main.py --sources "the-muse,remoteok" --locations "Alpharetta, GA;30005;Atlanta, GA;Remote" --show-all --min-score 0.5
```

7. **Load jobs from remote API:**

```bash
python c:\AA\DD\main.py --api-url https://example.com/api/jobs --threshold 0.75
```

## Key Options

- `--threshold`: Auto-apply score threshold (default: 0.75)
- `--show-all`: Display all jobs with scores (instead of auto-applying)
- `--min-score`: Minimum score to display (default: 0.5)
- `--top N`: Show full details for top N jobs
- `--view-job INDEX`: Show full details for job at index (0-indexed)
- `--details`: Show descriptions in job listings
- `--sources`: Comma-separated sources: `the-muse`, `remoteok`, `remotive`
- `--locations`: Semi-colon separated location queries
- `--pages`: Pages to fetch from The Muse (default: 1)
- `--api-url`: Remote JSON API endpoint
- `--profile`: Path to profile.json (auto-resolves in DD folder)
- `--jobs`: Path to jobs_sample.json (auto-resolves in DD folder)

## Job Details Display

When viewing job details, you'll see:

- **Match Score**: How well job matches your profile (0-100%)
- **Experience Required**: Years of experience needed
- **Key Skills**: Top skills for the role
- **Description**: Full job posting
- **Tags**: Job categories and type
- **Apply Link**: Direct URL to apply

## Output

5. Review generated output in `applications/`:

- `applications/resume.txt` - generated from your profile
- `applications/application_<job_id>.json` - application record for each job applied to

## Remote API format

The remote endpoint should return either a JSON list of jobs or an object with a top-level `jobs` list.
