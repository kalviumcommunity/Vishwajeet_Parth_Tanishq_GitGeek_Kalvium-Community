# Contributor Retention Analytics

A Sprint 1 MVP for the problem statement:

> Open-source maintainers have contributor activity, PR review timelines, and issue participation records, but no workflow reveals which onboarding experiences discourage first-time contributors from returning.

## What this MVP does

- Shows first-time contributor count, return rate, average response/review/merge times.
- Separates contributors into **Returned** and **Did not return**.
- Calculates onboarding factors from pull-request activity.
- Highlights possible drop-off factors.
- Generates maintainer recommendations from the observed data.
- Runs immediately in **Demo Mode** with sample data.
- Can analyze a public GitHub repository through the GitHub REST API.

## Tech stack

- Node.js + Express
- Vanilla HTML/CSS/JavaScript
- GitHub REST API
- Chart.js via CDN

## Run locally

1. Install Node.js 18+.
2. Open this folder in a terminal.
3. Run:

```bash
npm install
npm start
```

4. Open http://localhost:3000

## GitHub mode

Copy `.env.example` to `.env` and optionally add a GitHub personal access token:

```env
GITHUB_TOKEN=your_token_here
PORT=3000
```

Then enter a public repository such as `facebook/react` or `nodejs/node` in the dashboard.

### Important MVP limitation

GitHub's public API and repository history can be large. This MVP intentionally analyzes a bounded set of recent pull requests so it is easy to run during a sprint. For a production version, add pagination, caching, background jobs, database storage, GitHub App authentication, and a more rigorous cohort definition.

## Suggested Sprint 1 demo

1. Open the dashboard in Demo Mode.
2. Explain the onboarding funnel.
3. Show Returned vs Did Not Return.
4. Explain first response time, review activity, and merge time.
5. Show the factors panel and recommendations.
6. Switch to a public GitHub repo to demonstrate real-data analysis.

## Project structure

```text
contributor-retention-analytics/
├── public/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── data/
│   └── demo.json
├── .env.example
├── .gitignore
├── package.json
├── README.md
└── server.js
```
