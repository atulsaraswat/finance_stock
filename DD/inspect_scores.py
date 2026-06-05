from job_agent import JobAgent

agent = JobAgent(profile_path='profile.json', jobs_path='jobs_sample.json')
agent.load_profile()
agent.load_jobs_from_themuse(['Alpharetta, GA', 'Remote'], pages=3)
results = []
for job in agent.jobs:
    score = agent.score_job(job)
    results.append((score, job['title'], job['company'], job['location']))
results.sort(reverse=True)
for score, title, company, location in results[:20]:
    print(f"{score:.4f} | {company} | {title} | {location}")
print('total', len(results))
