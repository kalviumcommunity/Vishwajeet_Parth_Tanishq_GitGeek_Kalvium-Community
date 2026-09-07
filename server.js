require('dotenv').config();
const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const DEMO = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'demo.json'), 'utf8'));

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

function hoursBetween(a, b) {
  if (!a || !b) return null;
  return Math.max(0, (new Date(b) - new Date(a)) / 36e5);
}

function avg(values) {
  const clean = values.filter(v => Number.isFinite(v));
  return clean.length ? clean.reduce((a,b) => a+b, 0) / clean.length : 0;
}

function round(n, digits=1) {
  const p = 10 ** digits;
  return Math.round(n * p) / p;
}

function analyze(contributors, repo) {
  const total = contributors.length;
  const returned = contributors.filter(c => c.returned).length;
  const dropped = total - returned;
  const ret = total ? (returned / total) * 100 : 0;

  const factorDefs = [
    { key:'firstResponseHours', label:'Slow first response', direction:'high', threshold:48, unit:'hours', desc:'First maintainer response takes more than 48 hours.' },
    { key:'reviewHours', label:'Long review cycle', direction:'high', threshold:72, unit:'hours', desc:'First review takes more than 72 hours.' },
    { key:'mergeDays', label:'Slow merge', direction:'high', threshold:5, unit:'days', desc:'First PR remains open for more than 5 days.' },
    { key:'reviewRounds', label:'Many review rounds', direction:'high', threshold:3, unit:'rounds', desc:'Three or more review rounds can signal a difficult onboarding path.' },
    { key:'reviewComments', label:'Heavy review discussion', direction:'high', threshold:10, unit:'comments', desc:'Ten or more review comments indicate a high-feedback first PR.' },
    { key:'changesRequested', label:'Repeated changes requested', direction:'high', threshold:3, unit:'requests', desc:'Three or more requested changes may indicate unclear expectations.' }
  ];

  const factors = factorDefs.map(f => {
    const all = contributors.map(c => Number(c[f.key])).filter(Number.isFinite);
    const high = contributors.filter(c => Number(c[f.key]) >= f.threshold);
    const highReturned = high.filter(c => c.returned).length;
    const highRetention = high.length ? highReturned / high.length * 100 : 0;
    const low = contributors.filter(c => Number(c[f.key]) < f.threshold);
    const lowRetention = low.length ? low.filter(c => c.returned).length / low.length * 100 : 0;
    const gap = high.length > 0 ? round(lowRetention - highRetention) : 0;
    return {
      ...f,
      avg: round(avg(all)),
      highCount: high.length,
      highRetention: round(highRetention),
      lowRetention: round(lowRetention),
      gap
    };
  }).sort((a,b) => b.gap - a.gap);

  const recommendations = factors.filter(f => f.highCount > 0 && f.gap > 5).slice(0,4).map(f => ({
    title: f.label,
    text: `${f.highCount} contributors crossed the ${f.threshold} ${f.unit} threshold; their return rate was ${f.highRetention}% versus ${f.lowRetention}% for others.`,
    action: f.key === 'firstResponseHours' ? 'Create a first-time-contributor response SLA (for example, within 24–48 hours).' :
      f.key === 'reviewHours' ? 'Prioritize first-time-contributor PRs in the maintainer review queue.' :
      f.key === 'mergeDays' ? 'Add an onboarding label and fast-track small beginner PRs.' :
      f.key === 'reviewRounds' ? 'Improve contribution guidelines and provide examples before review begins.' :
      'Use clearer review checklists and explain requested changes with examples.'
  }));

  return {
    repo,
    total,
    returned,
    dropped,
    retentionRate: round(ret),
    avgFirstResponseHours: round(avg(contributors.map(c => Number(c.firstResponseHours)))),
    avgReviewHours: round(avg(contributors.map(c => Number(c.reviewHours)))),
    avgMergeDays: round(avg(contributors.map(c => Number(c.mergeDays)))),
    mergedRate: round(avg(contributors.map(c => c.merged ? 100 : 0))),
    factors,
    recommendations,
    contributors: contributors.map(c => ({...c, firstResponseHours: round(Number(c.firstResponseHours)), reviewHours: round(Number(c.reviewHours)), mergeDays: round(Number(c.mergeDays)), reviewComments: Number(c.reviewComments), reviewRounds: Number(c.reviewRounds), changesRequested: Number(c.changesRequested)}))
  };
}

async function gh(pathname) {
  const headers = { 'Accept':'application/vnd.github+json', 'User-Agent':'contributor-retention-analytics' };
  if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  const r = await fetch(`https://api.github.com${pathname}`, { headers });
  if (!r.ok) {
    const body = await r.text();
    throw new Error(`GitHub API ${r.status}: ${body.slice(0, 180)}`);
  }
  return r.json();
}

async function analyzeGithubRepo(repo) {
  if (!/^[^/]+\/[^/]+$/.test(repo)) throw new Error('Repository must look like owner/repository.');
  const prs = await gh(`/repos/${repo}/pulls?state=all&per_page=100&page=1&sort=created&direction=desc`);
  const byUser = new Map();
  for (const pr of prs) {
    if (!pr.user || pr.user.type === 'Bot') continue;
    if (!byUser.has(pr.user.login)) byUser.set(pr.user.login, []);
    byUser.get(pr.user.login).push(pr);
  }

  const firstTime = [...byUser.entries()].filter(([, arr]) => arr.length >= 1).map(([login, arr]) => {
    arr.sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
    return { login, first: arr[0], all: arr };
  }).slice(0, 25);

  const results = await Promise.all(firstTime.map(async (item) => {
    const pr = item.first;
    const [reviews, reviewComments, issueComments] = await Promise.all([
      gh(`/repos/${repo}/pulls/${pr.number}/reviews?per_page=100`).catch(() => []),
      gh(`/repos/${repo}/pulls/${pr.number}/comments?per_page=100`).catch(() => []),
      gh(`/repos/${repo}/issues/${pr.number}/comments?per_page=100`).catch(() => [])
    ]);

    const externalReviews = (reviews || []).filter(r => r.user && r.user.login !== item.login && r.submitted_at);
    const firstReview = externalReviews.sort((a,b) => new Date(a.submitted_at)-new Date(b.submitted_at))[0];
    const externalIssueComments = (issueComments || []).filter(c => c.user && c.user.login !== item.login && c.created_at);
    const firstResponse = externalIssueComments.sort((a,b) => new Date(a.created_at)-new Date(b.created_at))[0];
    const firstResponseTime = firstResponse ? hoursBetween(pr.created_at, firstResponse.created_at) : (firstReview ? hoursBetween(pr.created_at, firstReview.submitted_at) : 96);
    const reviewTime = firstReview ? hoursBetween(pr.created_at, firstReview.submitted_at) : firstResponseTime;
    const end = pr.merged_at || pr.closed_at || new Date().toISOString();
    const mergeDays = Math.max(0, hoursBetween(pr.created_at, end) / 24);
    const returned = item.all.some(other => other.number !== pr.number && new Date(other.created_at) > new Date(pr.created_at));
    const reviewRounds = new Set((reviews || []).map(r => r.user?.login + ':' + r.state)).size || (reviews || []).length || 0;
    return {
      login: item.login, firstPr: pr.number, returned,
      firstResponseHours: firstResponseTime,
      reviewHours: reviewTime,
      mergeDays,
      reviewComments: (reviewComments || []).length,
      reviewRounds,
      changesRequested: (reviews || []).filter(r => r.state === 'CHANGES_REQUESTED').length,
      issueComments: (issueComments || []).length,
      merged: Boolean(pr.merged_at)
    };
  }));
  return analyze(results, repo);
}

app.get('/api/demo', (req,res) => res.json(analyze(DEMO.contributors, DEMO.repo)));

app.get('/api/analyze', async (req,res) => {
  try {
    const repo = String(req.query.repo || '').trim();
    if (!repo) return res.status(400).json({error:'Provide a repository, e.g. facebook/react'});
    if (!/^[^/]+\/[^/]+$/.test(repo)) return res.status(400).json({error:'Repository must look like owner/repository.'});
    const result = await analyzeGithubRepo(repo);
    res.json(result);
  } catch (err) {
    const status = err.message && err.message.includes('404') ? 404 : 500;
    res.status(status).json({error: err.message});
  }
});

app.get('*', (req,res) => res.sendFile(path.join(__dirname,'public','index.html')));
app.listen(PORT, () => console.log(`Contributor Retention Analytics running at http://localhost:${PORT}`));
