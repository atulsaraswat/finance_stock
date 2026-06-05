import argparse
import os
import webbrowser

from job_agent import JobAgent


def main() -> None:
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    parser = argparse.ArgumentParser(
        description="Run the DD job agent and apply to matched jobs."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Minimum match score required to apply to a job (0.0-1.0).",
    )
    parser.add_argument(
        "--profile",
        default=os.path.join(script_dir, "profile.json"),
        help="Path to the user profile JSON file.",
    )
    parser.add_argument(
        "--jobs",
        default=os.path.join(script_dir, "jobs_sample.json"),
        help="Path to the jobs JSON file.",
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help="Optional remote JSON API endpoint that returns job listings.",
    )
    parser.add_argument(
        "--sources",
        default="the-muse,remoteok",
        help="Comma-separated job sources to query: the-muse, remoteok, remotive.",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to fetch from The Muse for each location.",
    )
    parser.add_argument(
        "--locations",
        default="Alpharetta, GA;30005;Atlanta, GA;Johns Creek, GA;Duluth, GA;Roswell, GA;Suwanee, GA;Remote",
        help="Semi-colon separated location queries for The Muse API.",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Display all evaluated jobs with scores (not just applied ones).",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.5,
        help="Minimum match score to display when using --show-all (0.0-1.0).",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Show detailed job descriptions and skills.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="Show full details for top N matching jobs (0=disabled).",
    )
    parser.add_argument(
        "--view-job",
        type=int,
        default=-1,
        help="View full details for job at index N (sorted by match score, 0-indexed).",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open job link in browser (use with --view-job or --threshold).",
    )

    args = parser.parse_args()

    agent = JobAgent(profile_path=args.profile, jobs_path=args.jobs)
    agent.load_profile()
    sources = [source.strip().lower() for source in args.sources.split(",") if source.strip()]
    locations = [loc.strip() for loc in args.locations.split(";") if loc.strip()]
    agent.jobs = []
    if sources:
        if "the-muse" in sources:
            muse_jobs = agent.load_jobs_from_themuse(locations=locations, pages=args.pages)
            agent.add_jobs(muse_jobs)
        if "remoteok" in sources:
            remoteok_jobs = agent.load_jobs_from_remoteok()
            agent.add_jobs(remoteok_jobs)
        if "remotive" in sources:
            try:
                remotive_jobs = agent.load_jobs_from_api("https://remotive.io/api/remote-jobs")
                agent.add_jobs(remotive_jobs)
            except Exception as exc:
                print(f"Warning: Remotive source failed: {exc}")
    if not agent.jobs:
        if args.api_url:
            agent.jobs = agent.load_jobs_from_api(args.api_url)
        else:
            agent.load_jobs()
    
    if args.view_job >= 0:
        # View a specific job by index
        scored = agent.score_all_jobs()
        if 0 <= args.view_job < len(scored):
            job = scored[args.view_job]
            agent.display_job_details(job)
            if args.open:
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
                    webbrowser.open(url)
                    print(f"Opened: {url}")
                else:
                    print("No URL available for this job.")
        else:
            print(f"Job index {args.view_job} out of range. Available: 0-{len(scored)-1}")
    elif args.show_all:
        scored = agent.score_all_jobs()
        filtered = [job for job in scored if job["match_score"] >= args.min_score]
        print(f"\n{'='*110}")
        print(f"EVALUATED JOBS (min score: {args.min_score})")
        print(f"{'='*110}")
        agent.display_jobs(filtered, show_details=args.details)
        print(f"\n{len(filtered)} jobs match minimum score of {args.min_score:.2f}")
        
        # Show top N jobs with full details
        if args.top > 0:
            print(f"\n{'='*110}")
            print(f"TOP {args.top} JOBS - FULL DETAILS")
            print(f"{'='*110}")
            for i, job in enumerate(filtered[:args.top]):
                print(f"\n[{i+1}] ", end="")
                agent.display_job_details(job)
    else:
        applied_jobs = agent.run(threshold=args.threshold)
        print(f"\nApplied to {len(applied_jobs)} job(s) with threshold {args.threshold:.2f}.")
        
        # Show full details for each applied job
        for i, job in enumerate(applied_jobs, 1):
                print(f"\n[Application {i}]")
                agent.display_job_details(job)
                if args.open:
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
                        webbrowser.open(url)
                        print(f"Opened: {url}")
                    else:
                        print("No URL available for this job.")


if __name__ == "__main__":
    main()
