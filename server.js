
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
  return clean.length ? clean.reduce((a, b) => a + b, 0) / clean.length : 0;
}

function round(n, digits = 1) {
  const p = 10 ** digits;
  return Math.round(n * p) / p;
}

function analyze(contributors, repo) {
  const total = contributors.length;
  const returned = contributors.filter(c => c.returned).length;
  const dropped = total - returned;
  const ret = total ? (returned / total) * 100 : 0;

  const factorDefs = [
    {
      key: 'firstResponseHours',
      label: 'Slow first response',
      direction: 'high',
      threshold: 48,
      unit: 'hours',
      desc: 'First maintainer response takes more than 48 hours.'
    },
    {
      key: 'reviewHours',
      label: 'Long review cycle',
      direction: 'high',
      threshold: 72,
      unit: 'hours',
      desc: 'First review takes more than 72 hours.'
    },
    {
      key: 'mergeDays',
      label: 'Slow merge',
      direction: 'high',
      threshold: 5,
      unit: 'days',
      desc: 'First PR remains open for more than 5 days.'
    },
    {
      key: 'reviewRounds',
      label: 'Many review rounds',
      direction: 'high',
      threshold: 3,
      unit: 'rounds',
      desc: 'Three or more review interactions can signal a difficult onboarding path.'
    },
    {
      key: 'reviewComments',
      label: 'Heavy review discussion',
      direction: 'high',
      threshold: 10,
      unit: 'comments',
      desc: 'Ten or more review comments indicate a high-feedback first PR.'
    },
    {
      key: 'changesRequested',
      label: 'Repeated changes requested',
      direction: 'high',
      threshold: 3,
      unit: 'requests',
      desc: 'Three or more requested changes may indicate unclear expectations.'
    }
  ];

  const factors = factorDefs.map(f => {
    const all = contributors
      .map(c => Number(c[f.key]))
      .filter(Number.isFinite);

    const high = contributors.filter(
      c => Number(c[f.key]) >= f.threshold
    );

    const highReturned = high.filter(c => c.returned).length;
    const highRetention = high.length
      ? (highReturned / high.length) * 100
      : 0;

    const low = contributors.filter(
      c => Number(c[f.key]) < f.threshold
    );

    const lowRetention = low.length
      ? (low.filter(c => c.returned).length / low.length) * 100
      : 0;

    const gap = high.length
      ? round(lowRetention - highRetention)
      : 0;

    return {
      ...f,
      avg: round(avg(all)),
      highCount: high.length,
      highRetention: round(highRetention),
      lowRetention: round(lowRetention),
      gap
    };
  }).sort((a, b) => b.gap - a.gap);

  const recommendations = factors
    .filter(f => f.highCount > 0 && f.gap > 5)
    .slice(0, 4)
    .map(f => ({
      title: f.label,
      text: `${f.highCount} contributors crossed the ${f.threshold} ${f.unit} threshold; their return rate was ${f.highRetention}% versus ${f.lowRetention}% for others.`,
      action:
        f.key === 'firstResponseHours'
          ? 'Create a first-time-contributor response SLA (for example, within 24–48 hours).'
          : f.key === 'reviewHours'
            ? 'Prioritize first-time-contributor PRs in the maintainer review queue.'
            : f.key === 'mergeDays'
              ? 'Add an onboarding label and fast-track small beginner PRs.'
              : f.key === 'reviewRounds'
                ? 'Improve contribution guidelines and provide examples before review begins.'
                : 'Use clearer review checklists and explain requested changes with examples.'
    }));

  return {
    repo,
    total,
    returned,
    dropped,
    retentionRate: round(ret),
    avgFirstResponseHours: round(
      avg(contributors.map(c => Number(c.firstResponseHours)))
    ),
    avgReviewHours: round(
      avg(contributors.map(c => Number(c.reviewHours)))
    ),
    avgMergeDays: round(
      avg(contributors.map(c => Number(c.mergeDays)))
    ),
    mergedRate: round(
      avg(contributors.map(c => c.merged ? 100 : 0))
    ),
    factors,
    recommendations,
    contributors: contributors.map(c => ({
      ...c,
      firstResponseHours: round(Number(c.firstResponseHours)),
      reviewHours: round(Number(c.reviewHours)),
      mergeDays: round(Number(c.mergeDays)),
      reviewComments: Number(c.reviewComments),
      reviewRounds: Number(c.reviewRounds),
      changesRequested: Number(c.changesRequested),
      issueComments: Number(c.issueComments)
    }))
  };
}

async function gh(pathname) {
  const headers = {
    Accept: 'application/vnd.github+json',
    'User-Agent': 'contributor-retention-analytics'
  };

  if (process.env.GITHUB_TOKEN) {
    headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  }

  const response = await fetch(
    `https://api.github.com${pathname}`,
    { headers }
  );

  if (!response.ok) {
    const body = await response.text();
    throw new Error(
      `GitHub API ${response.status}: ${body.slice(0, 180)}`
    );
  }

  return response.json();
}

async function ghAll(pathname, maxPages = 2) {
  const results = [];

  for (let page = 1; page <= maxPages; page++) {
    const separator = pathname.includes('?') ? '&' : '?';

    const pageData = await gh(
      `${pathname}${separator}per_page=100&page=${page}`
    );

    if (!Array.isArray(pageData) || pageData.length === 0) {
      break;
    }

    results.push(...pageData);

    if (pageData.length < 100) {
      break;
    }
  }

  return results;
}

async function analyzeGithubRepo(repo) {
  if (!/^[^/]+\/[^/]+$/.test(repo)) {
    throw new Error('Repository must look like owner/repository.');
  }

  const prs = await ghAll(
    `/repos/${repo}/pulls?state=all&sort=created&direction=asc`,
    3
  );

  const byUser = new Map();

  for (const pr of prs) {
    if (!pr.user || pr.user.type === 'Bot') continue;

    if (!byUser.has(pr.user.login)) {
      byUser.set(pr.user.login, []);
    }

    byUser.get(pr.user.login).push(pr);
  }

  const firstTime = [...byUser.entries()]
    .map(([login, arr]) => {
      arr.sort(
        (a, b) =>
          new Date(a.created_at) - new Date(b.created_at)
      );

      return {
        login,
        first: arr[0],
        all: arr
      };
    })
    .slice(0, 10);

  const results = [];

  for (const item of firstTime) {
    const pr = item.first;

    const [reviews, reviewComments, issueComments] = await Promise.all([
      ghAll(`/repos/${repo}/pulls/${pr.number}/reviews`, 1).catch(() => []),
      ghAll(`/repos/${repo}/pulls/${pr.number}/comments`, 1).catch(() => []),
      ghAll(`/repos/${repo}/issues/${pr.number}/comments`, 1).catch(() => [])
    ]);

    const externalReviews = (reviews || [])
      .filter(
        r =>
          r.user &&
          r.user.login !== item.login &&
          r.submitted_at
      )
      .sort(
        (a, b) =>
          new Date(a.submitted_at) -
          new Date(b.submitted_at)
      );

    const firstReview = externalReviews[0];

    const externalIssueComments = (issueComments || [])
      .filter(
        c =>
          c.user &&
          c.user.login !== item.login &&
          c.created_at
      )
      .sort(
        (a, b) =>
          new Date(a.created_at) -
          new Date(b.created_at)
      );

    const firstResponse = externalIssueComments[0];

    const firstResponseTime = firstResponse
      ? hoursBetween(
          pr.created_at,
          firstResponse.created_at
        )
      : firstReview
        ? hoursBetween(
            pr.created_at,
            firstReview.submitted_at
          )
        : null;

    const reviewTime = firstReview
      ? hoursBetween(
          pr.created_at,
          firstReview.submitted_at
        )
      : firstResponseTime;

    const end =
      pr.merged_at ||
      pr.closed_at ||
      new Date().toISOString();

    const mergeDays = Math.max(
      0,
      hoursBetween(pr.created_at, end) / 24
    );

    const returned = item.all.some(
      other =>
        other.number !== pr.number &&
        new Date(other.created_at) >
          new Date(pr.created_at)
    );

    const reviewerInteractions = externalReviews;

    const reviewRounds = reviewerInteractions.length;

    const changesRequested = (reviews || []).filter(
      r =>
        r.user &&
        r.user.login !== item.login &&
        r.state === 'CHANGES_REQUESTED'
    ).length;

    results.push({
      login: item.login,
      firstPr: pr.number,
      returned,
      firstResponseHours: firstResponseTime ?? 96,
      reviewHours: reviewTime ?? 96,
      mergeDays,
      reviewComments: (reviewComments || []).filter(
        c =>
          c.user &&
          c.user.login !== item.login
      ).length,
      reviewRounds,
      changesRequested,
      issueComments: (issueComments || []).length,
      merged: Boolean(pr.merged_at),
      noMaintainerResponse: !firstResponse && !firstReview
    });
  }

  return analyze(results, repo);
}

app.get('/api/demo', (req, res) => {
  res.json(
    analyze(
      DEMO.contributors,
      DEMO.repo
    )
  );
});

app.get('/api/analyze', async (req, res) => {
  try {
    const repo = String(req.query.repo || '').trim();

    if (!repo) {
      return res.status(400).json({
        error: 'Provide a repository, e.g. facebook/react'
      });
    }

    if (!/^[^/]+\/[^/]+$/.test(repo)) {
      return res.status(400).json({
        error: 'Repository must look like owner/repository.'
      });
    }

    const result = await analyzeGithubRepo(repo);

    res.json(result);
  } catch (err) {
    const message = err.message || 'Analysis failed.';
    const status = message.includes('404') ? 404 : 500;

    res.status(status).json({
      error: message
    });
  }
});

app.get('*', (req, res) => {
  res.sendFile(
    path.join(
      __dirname,
      'public',
      'index.html'
    )
  );
});

app.listen(PORT, () => {
  console.log(
    `Contributor Retention Analytics running at http://localhost:${PORT}`
  );
});

