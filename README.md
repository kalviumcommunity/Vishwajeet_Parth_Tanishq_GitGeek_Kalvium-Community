# Contributor Retention Analytics

A Sprint 1 MVP that helps open-source maintainers understand why first-time contributors return or drop off after their initial contribution.

## Problem Statement

Open-source maintainers have access to contributor activity, pull request timelines, review discussions, and issue participation data, but they often lack insights into which onboarding experiences discourage first-time contributors from returning.

Contributor Retention Analytics analyzes contributor journeys and identifies possible friction points in the onboarding process.

---

# Features

## Contributor Retention Dashboard

The dashboard provides an overview of contributor onboarding metrics:

- Total first-time contributors analyzed
- Contributor return rate
- Average first maintainer response time
- Average PR merge time
- Returned vs dropped-off contributor comparison


## GitHub Repository Analysis

The application can analyze public GitHub repositories using the GitHub REST API.

Example repositories:


facebook/react
nodejs/node
expressjs/express


The system collects pull request activity and contributor interaction data to generate insights.


## Drop-off Factor Detection

The system analyzes different onboarding signals:

- Slow first maintainer response
- Long review cycles
- Slow PR merging
- Multiple review rounds
- Heavy review discussions
- Repeated change requests

These factors are compared between contributors who returned and contributors who did not.


## Maintainer Recommendations

Based on observed contributor behavior, the application generates possible actions such as:

- Improving first response time
- Prioritizing first-time contributor PR reviews
- Creating clearer contribution guidelines
- Reducing onboarding friction


## Demo Mode

The application includes built-in demo data so the dashboard can be explored without connecting to GitHub.

---

# Tech Stack

## Backend

- Node.js
- Express.js
- GitHub REST API


## Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Chart.js


## Other Tools

- dotenv for environment configuration
- GitHub Personal Access Token authentication

---

# Application Flow


GitHub Repository
|
|
v
GitHub REST API
|
|
v
Pull Request & Contributor Data
|
|
v
Analytics Engine
|
|
v
Retention Insights Dashboard


---

# How It Works

1. User enters a public GitHub repository.

Example:


owner/repository


2. The application fetches pull request information.

3. Contributors are grouped based on their first contribution.

4. Contributor activity is analyzed:

- Response time
- Review activity
- Merge duration
- Future contribution activity

5. Contributors are classified into:


Returned


or


Did not return


6. The system compares both groups and identifies possible onboarding problems.

---

# Installation & Setup

## Prerequisites

Make sure you have:

- Node.js 18+
- npm installed


## Clone Repository

```bash
git clone <repository-url>

Move into the project folder:

cd contributor-retention-analytics
Install Dependencies
npm install
Environment Setup

Create a .env file:

cp .env.example .env

Add your configuration:

GITHUB_TOKEN=your_github_token_here
PORT=3000

A GitHub token is optional but recommended because authenticated requests have higher API rate limits.

Running the Application

Start the server:

npm start

Open:

http://localhost:3000
Project Structure
contributor-retention-analytics/

├── public/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── data/
│   └── demo.json
│
├── .env.example
├── .gitignore
├── package.json
├── README.md
└── server.js
Dashboard Sections
KPI Overview

Displays:

Contributor count
Retention percentage
Average response time
Average merge time
Retention Chart

Visualizes:

Contributors who returned
Contributors who stopped contributing
Experience Comparison

Compares returned and dropped contributors across:

Response time
Review time
Review rounds
Merge duration
Friction Factors

Highlights onboarding factors that show correlation with contributor drop-off.

Contributor Table

Shows individual contributor profiles:

Username
Retention status
Response time
Review duration
Merge status
GitHub API Usage

This project uses GitHub REST API endpoints to collect:

Pull requests
Reviews
Review comments
Issue comments
Contributor activity

Because GitHub repositories can contain thousands of pull requests, this MVP intentionally analyzes a limited dataset for faster execution.

Current Limitations

This is a Sprint 1 MVP and has some limitations:

Uses a bounded number of pull requests
Does not store historical analytics
No background monitoring jobs
No database persistence
No GitHub App authentication
Retention definition is simplified
Large repositories may take longer to analyze
Future Improvements

Possible improvements for a production-level version:

Data & Backend
Add database storage
Add background analysis jobs
Implement caching
Add GitHub App authentication
Store repository history
Analytics
More accurate contributor cohort detection
Machine learning based retention prediction
Contributor onboarding scoring
Trend analysis over time
Product Features
User accounts
Saved repositories
Scheduled repository monitoring
Email/Slack alerts
Maintainer dashboards
Sprint 1 Demo Flow

Recommended presentation flow:

Open the dashboard in Demo Mode
Explain the contributor onboarding problem
Show:
Contributor count
Retention rate
Returned vs dropped contributors
Explain detected friction factors
Show recommended maintainer actions
Analyze a real GitHub repository

Example:

expressjs/express
Team / Project Information
Project

Contributor Retention Analytics

Version

Sprint 1 MVP

Purpose

Helping open-source maintainers understand contributor onboarding experiences and identify possible reasons behind contributor drop-off.

License

This project is created for educational and academic purposes.
