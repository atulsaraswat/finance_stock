import json
import os
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List


class JobAgent:
    def __init__(self, profile_path: str, jobs_path: str) -> None:
        self.profile_path = profile_path
        self.jobs_path = jobs_path
        self.profile: Dict[str, Any] = {}
        self.jobs: List[Dict[str, Any]] = []
        self.applications_dir = os.path.join(os.path.dirname(__file__), "applications")
        self.resume_file = os.path.join(self.applications_dir, "resume.txt")

    def load_profile(self) -> None:
        with open(self.profile_path, "r", encoding="utf-8") as handle:
            self.profile = json.load(handle)

    def load_jobs(self) -> None:
        with open(self.jobs_path, "r", encoding="utf-8") as handle:
            self.jobs = json.load(handle)

    def load_jobs_from_api(self, api_url: str) -> List[Dict[str, Any]]:
        request = urllib.request.Request(api_url, headers={"User-Agent": "DDJobAgent/1.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        if isinstance(data, dict) and "jobs" in data:
            return data["jobs"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("Remote API response did not contain a valid list of jobs.")

    def load_jobs_from_remoteok(self) -> List[Dict[str, Any]]:
        url = "https://remoteok.com/api"
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        jobs: List[Dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if item.get("id") is None:
                continue
            jobs.append(self.transform_remoteok_job(item))
        return jobs

    def transform_remoteok_job(self, item: Dict[str, Any]) -> Dict[str, Any]:
        tags = [str(tag).lower() for tag in item.get("tags", []) if tag]
        location = str(item.get("location", "")).strip()
        if not location and str(item.get("remote", "")).lower() in {"true", "1"}:
            location = "Remote"

        return {
            "id": item.get("id"),
            "title": item.get("position"),
            "company": item.get("company"),
            "location": location,
            "description": item.get("description", ""),
            "skills": tags,
            "tags": tags + ([str(item.get("job_type"))] if item.get("job_type") else []),
            "minimum_years_experience": 3,
            "refs": {
                "url": item.get("url") or item.get("application_url"),
            },
        }

    def transform_themuse_job(self, item: Dict[str, Any]) -> Dict[str, Any]:
        location_names = [loc.get("name", "") for loc in item.get("locations", [])]
        location = ", ".join([name for name in location_names if name])

        tags = [cat.get("name", "") for cat in item.get("categories", [])]
        tags += [dom.get("name", "") for dom in item.get("domains", [])]
        if item.get("job_type"):
            tags.append(item["job_type"])

        level_names = [lvl.get("name", "").lower() for lvl in item.get("levels", [])]
        if any("senior" in lvl for lvl in level_names):
            minimum_years_experience = 6
        elif any("mid" in lvl or "experienced" in lvl for lvl in level_names):
            minimum_years_experience = 4
        elif any("entry" in lvl or "junior" in lvl for lvl in level_names):
            minimum_years_experience = 1
        else:
            minimum_years_experience = 3

        skills = [tag for tag in tags if tag]
        return {
            "id": item.get("id"),
            "title": item.get("name"),
            "company": item.get("company", {}).get("name"),
            "location": location,
            "description": item.get("contents", ""),
            "skills": skills,
            "tags": skills,
            "minimum_years_experience": minimum_years_experience,
            "refs": item.get("refs", {}),
        }

    def load_jobs_from_themuse(self, locations: List[str], pages: int = 1) -> List[Dict[str, Any]]:
        jobs: List[Dict[str, Any]] = []
        headers = {"User-Agent": "Mozilla/5.0"}
        for location in locations:
            for page in range(1, pages + 1):
                query = urllib.parse.urlencode({"location": location, "page": page})
                url = f"https://www.themuse.com/api/public/jobs?{query}"
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request, timeout=20) as response:
                    data = json.loads(response.read().decode("utf-8"))
                for item in data.get("results", []):
                    jobs.append(self.transform_themuse_job(item))

        seen = set()
        unique_jobs: List[Dict[str, Any]] = []
        for job in jobs:
            job_id = job.get("id")
            if job_id and job_id not in seen:
                seen.add(job_id)
                unique_jobs.append(job)
        self.jobs = unique_jobs
        return self.jobs

    def add_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        existing_ids = {job.get("id") for job in self.jobs if job.get("id")}
        for job in jobs:
            job_id = job.get("id")
            if job_id and job_id not in existing_ids:
                self.jobs.append(job)
                existing_ids.add(job_id)

    def save_resume(self) -> str:
        os.makedirs(self.applications_dir, exist_ok=True)
        resume_text = self.generate_resume_text()
        with open(self.resume_file, "w", encoding="utf-8") as handle:
            handle.write(resume_text)
        return self.resume_file

    def generate_resume_text(self) -> str:
        skills = ", ".join(self.profile.get("skills", []))
        industries = ", ".join(self.profile.get("industry_experience", []))
        return (
            f"Name: {self.profile.get('name')}\n"
            f"Title: {self.profile.get('title')}\n"
            f"Location: {self.profile.get('location')}\n"
            f"Years Experience: {self.profile.get('years_experience')}\n\n"
            f"Summary:\n{self.profile.get('summary')}\n\n"
            f"Skills:\n{skills}\n\n"
            f"Industry Experience:\n{industries}\n"
        )

    def normalize_text(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

    def build_profile_terms(self) -> List[str]:
        terms = []
        if not self.profile:
            return terms

        fields = [
            self.profile.get("title", ""),
            self.profile.get("summary", ""),
            " ".join(self.profile.get("skills", [])),
            " ".join(self.profile.get("industry_experience", [])),
            self.profile.get("location", ""),
        ]
        for value in fields:
            terms.extend(self.normalize_text(str(value)).split())

        return sorted(set(terms))

    def score_job(self, job: Dict[str, Any]) -> float:
        profile_terms = self.build_profile_terms()

        job_text = " ".join(
            [
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("description", ""),
                " ".join(job.get("skills", [])),
                " ".join(job.get("tags", [])),
            ]
        )
        normalized_job_text = self.normalize_text(job_text)
        job_tokens = set(normalized_job_text.split())

        if not profile_terms or not job_tokens:
            return 0.0

        matches = [term for term in profile_terms if term in job_tokens]
        keyword_score = len(matches) / max(len(profile_terms), 1)

        profile_years = float(self.profile.get("years_experience", 0))
        job_years = float(job.get("minimum_years_experience", 0))
        if job_years <= profile_years:
            experience_match = 1.0
        else:
            experience_match = max(0.0, 1.0 - (job_years - profile_years) / max(job_years, 1))

        profile_location = str(self.profile.get("location", "")).lower()
        job_location = str(job.get("location", "")).lower()
        location_match = 0.5
        if profile_location and profile_location in job_location:
            location_match = 1.0
        elif job_location and job_location in profile_location:
            location_match = 1.0
        if "remote" in profile_location or "remote" in job_location:
            location_match = 1.0
        if "ga" in profile_location and "ga" in job_location:
            location_match = max(location_match, 1.0)

        seniority_terms = [
            "director",
            "architect",
            "principal",
            "senior",
            "lead",
            "head",
            "staff",
            "manager",
        ]
        job_title = self.normalize_text(str(job.get("title", "")))
        profile_title = self.normalize_text(str(self.profile.get("title", "")))
        seniority_match = 0.0
        if any(term in job_title for term in seniority_terms):
            if any(term in profile_title for term in seniority_terms):
                seniority_match = 1.0
            else:
                seniority_match = 0.75

        cloud_ai_terms = [
            "azure",
            "aws",
            "gcp",
            "oci",
            "terraform",
            "kubernetes",
            "docker",
            "ai",
            "ml",
            "agentic",
            "cloud",
            "security",
            "devops",
            "sre",
            "reliability",
        ]
        domain_matches = [term for term in cloud_ai_terms if term in job_tokens]
        domain_bonus = min(1.0, len(domain_matches) / 5.0)

        score = (
            keyword_score * 0.38
            + experience_match * 0.25
            + location_match * 0.15
            + seniority_match * 0.12
            + domain_bonus * 0.10
        )
        return min(max(score, 0.0), 1.0)

    def score_all_jobs(self) -> List[Dict[str, Any]]:
        """Score all jobs and return them with scores in descending order."""
        scored_jobs: List[Dict[str, Any]] = []
        for job in self.jobs:
            score = self.score_job(job)
            job_copy = dict(job)
            job_copy["match_score"] = round(score, 4)
            scored_jobs.append(job_copy)
        return sorted(scored_jobs, key=lambda j: j["match_score"], reverse=True)

    def filter_jobs(self, threshold: float) -> List[Dict[str, Any]]:
        scored = self.score_all_jobs()
        return [job for job in scored if job["match_score"] >= threshold]

    def display_jobs(self, jobs: List[Dict[str, Any]], show_details: bool = False) -> None:
        """Print job listings in a readable format."""
        if not jobs:
            print("No jobs to display.")
            return

        print(f"\n{'Match %':<8} {'Score':<7} {'Title':<40} {'Company':<25} {'Location':<20}")
        print("-" * 110)
        
        for job in jobs:
            score = job.get("match_score", 0.0)
            match_pct = f"{score * 100:.1f}%"
            title = str(job.get("title", ""))[:38]
            company = str(job.get("company", ""))[:23]
            location = str(job.get("location", ""))[:18]
            
            print(f"{match_pct:<8} {score:<7.4f} {title:<40} {company:<25} {location:<20}")
            
            if show_details:
                print(f"  Description: {job.get('description', '')[:100]}...")
                print(f"  Skills: {', '.join(job.get('skills', [])[:5])}")
                print()

    def display_job_details(self, job: Dict[str, Any]) -> None:
        """Print comprehensive details for a single job."""
        print("\n" + "=" * 100)
        print(f"JOB DETAILS")
        print("=" * 100)
        
        # Header
        print(f"\n📌 {job.get('title', 'N/A')}")
        print(f"   Company: {job.get('company', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Match Score: {job.get('match_score', 0):.1%} ⭐")
        
        # Experience
        print(f"\n👨‍💼 Experience Required: {job.get('minimum_years_experience', 'N/A')} years")
        
        # Skills
        skills = job.get('skills', [])
        if skills:
            print(f"\n🔧 Key Skills:")
            for skill in skills[:10]:
                print(f"   • {skill}")
        
        # Description
        description = job.get('description', '')
        if description:
            # Truncate to first 1000 chars for readability, but show meaningful content
            if len(description) > 1000:
                description = description[:1000] + "..."
            print(f"\n📝 Description:")
            print(f"   {description}")
        
        # Tags
        tags = job.get('tags', [])
        if tags:
            print(f"\n🏷️  Tags: {', '.join(tags[:8])}")
        
        # URL
        refs = job.get('refs', {})
        url = None
        if isinstance(refs, dict):
            url = (
                refs.get('url')
                or refs.get('application_url')
                or refs.get('apply_url')
                or refs.get('redirect_url')
                or refs.get('landing_page_url')
                or refs.get('job_url')
            )
        if url:
            print(f"\n🔗 Apply here: {url}")
        else:
            print(f"\n🔗 Apply here: No URL available")
        
        print("\n" + "=" * 100 + "\n")

    def apply_to_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        os.makedirs(self.applications_dir, exist_ok=True)
        application_record = {
            "job_id": job.get("id"),
            "company": job.get("company"),
            "title": job.get("title"),
            "location": job.get("location"),
            "match_score": job.get("match_score"),
            "profile_name": self.profile.get("name"),
            "resume_file": os.path.basename(self.resume_file),
            "message": self.build_application_message(job),
        }

        output_path = os.path.join(self.applications_dir, f"application_{job.get('id')}.json")
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(application_record, handle, indent=2)

        # Return the full job object for display purposes
        return job

    def build_application_message(self, job: Dict[str, Any]) -> str:
        return (
            f"Dear hiring team at {job.get('company')},\n\n"
            f"I am excited to apply for the {job.get('title')} role. With {self.profile.get('years_experience')} years of experience in {', '.join(self.profile.get('industry_experience', []))}, "
            f"I have worked with {', '.join(self.profile.get('skills', []))} and am confident in my ability to contribute to your team.\n\n"
            f"Thank you for considering my application.\n\n"
            f"Best regards,\n{self.profile.get('name')}"
        )

    def run(self, threshold: float) -> List[Dict[str, Any]]:
        self.save_resume()
        matches = self.filter_jobs(threshold=threshold)
        applied: List[Dict[str, Any]] = []
        for job in matches:
            application = self.apply_to_job(job)
            applied.append(application)
        return applied
