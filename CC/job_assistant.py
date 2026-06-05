import json
import yaml
from pathlib import Path


class JobAssistant:
    def __init__(self, profile_path, sites=None, threshold=0.75):
        self.profile_path = Path(profile_path)
        self.sites = sites or []
        self.threshold = threshold
        self.profile = self.load_profile()

    def load_profile(self):
        if not self.profile_path.exists():
            raise FileNotFoundError(f"Profile not found: {self.profile_path}")

        if self.profile_path.suffix.lower() in {".yaml", ".yml"}:
            with self.profile_path.open("r", encoding="utf-8") as fh:
                return yaml.safe_load(fh)

        with self.profile_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def run(self):
        print(f"Loaded profile: {self.profile_path}")
        print(f"Searching sites: {self.sites}")
        for site in self.sites:
            jobs = self.search_site(site)
            for job in jobs:
                score = self.match_score(job)
                if score >= self.threshold:
                    print(f"Matched {job['title']} at {site} (score={score:.2f})")
                    self.apply(job, site)

    def search_site(self, site):
        print(f"Searching jobs on {site}...")
        # TODO: implement actual site-specific search logic
        return []

    def match_score(self, job):
        print(f"Evaluating match for job: {job.get('title')}")
        # TODO: implement actual matching logic based on profile and job data
        return 0.0

    def apply(self, job, site):
        print(f"Applying for job: {job.get('title')} on {site}")
        # TODO: implement automated application flow for supported sites


if __name__ == "__main__":
    raise SystemExit("Run this module through main.py")
