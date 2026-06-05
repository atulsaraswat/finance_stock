import argparse
from job_assistant import JobAssistant


def parse_args():
    parser = argparse.ArgumentParser(description="CC Job Match Assistant")
    parser.add_argument("--profile", required=True, help="Path to the user profile JSON or YAML file")
    parser.add_argument("--sites", nargs="*", default=["example"], help="List of job sites to search")
    parser.add_argument("--threshold", type=float, default=0.75, help="Match threshold from 0.0 to 1.0")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    assistant = JobAssistant(profile_path=args.profile, sites=args.sites, threshold=args.threshold)
    assistant.run()
