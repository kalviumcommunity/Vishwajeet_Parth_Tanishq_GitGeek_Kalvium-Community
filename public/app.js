let data = null;
let retentionChart = null;
let comparisonChart = null;

const $ = id => document.getElementById(id);
const fmtHours = n => n >= 24 ? `${(n/24).toFixed(1)}d` : `${n.toFixed(1)}h`;
const fmtDays = n => `${n.toFixed(1)}d`;
const DEFAULT_REPO = 'expressjs/express';

function setLoading(on){ $('loading').classList.toggle('hidden', !on); $('error').classList.add('hidden'); }
function showError(msg){ $('loading').classList.add('hidden'); $('error').textContent = msg; $('error').classList.remove('hidden'); }


function render(d, mode='Demo Mode') {
  data = d;
  $('modeText').textContent = mode;
  $('total').textContent = d.total;
  $('retention').textContent = `${d.retentionRate}%`;
  $('firstResponse').textContent = fmtHours(d.avgFirstResponseHours);
  $('mergeDays').textContent = fmtDays(d.avgMergeDays);
  $('donutRate').textContent = `${d.retentionRate}%`;
  $('returnedCount').textContent = d.returned;
  $('droppedCount').textContent = d.dropped;

  if(retentionChart) retentionChart.destroy();
  retentionChart = new Chart($('retentionChart'), {type:'doughnut', data:{labels:['Returned','Did not return'],datasets:[{data:[d.returned,d.dropped],backgroundColor:['#5b5ce2','#e3e6ed'],borderWidth:0}]},options:{cutout:'74%',plugins:{legend:{display:false}}}});

  const r = d.contributors.filter(c=>c.returned), x = d.contributors.filter(c=>!c.returned);
  const metrics = [
    ['First response (h)', r.map(c=>c.firstResponseHours), x.map(c=>c.firstResponseHours)],
    ['Review time (h)', r.map(c=>c.reviewHours), x.map(c=>c.reviewHours)],
    ['Review rounds', r.map(c=>c.reviewRounds), x.map(c=>c.reviewRounds)],
    ['Merge time (d)', r.map(c=>c.mergeDays), x.map(c=>c.mergeDays)]
  ];
  if(comparisonChart) comparisonChart.destroy();
  comparisonChart = new Chart($('comparisonChart'), {type:'bar',data:{labels:metrics.map(m=>m[0]),datasets:[{label:'Returned',data:metrics.map(m=>avg(m[1])),backgroundColor:'#5b5ce2',borderRadius:5},{label:'Did not return',data:metrics.map(m=>avg(m[2])),backgroundColor:'#dfe2e9',borderRadius:5}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{font:{size:10}}}},scales:{x:{grid:{display:false},ticks:{font:{size:9}}},y:{beginAtZero:true,grid:{color:'#eef0f4'},ticks:{font:{size:9}}}}}});

  $('factors').innerHTML = d.factors.map(f => {
    const width = Math.min(100, Math.max(8, Math.abs(f.gap)));
    return `<div class="factor"><div><div class="factor-title">${f.label}</div><div class="factor-desc">${f.desc}</div></div><div class="bar"><span style="width:${width}%"></span></div><div class="factor-stat"><strong>${f.gap > 0 ? f.gap+' pts' : 'Low signal'}</strong>${f.highCount} above threshold</div></div>`;
  }).join('');

  $('recommendations').innerHTML = d.recommendations.length ? d.recommendations.map(x => `<article class="recommendation"><h3>${x.title}</h3><p>${x.text}</p><div class="action">→ ${x.action}</div></article>`).join('') : '<div class="empty">No strong friction factor crossed the evidence threshold in this cohort. Collect more data before making a recommendation.</div>';
  renderTable();
}

function avg(a){const v=a.filter(Number.isFinite);return v.length?v.reduce((x,y)=>x+y,0)/v.length:0}
function renderTable(){
  if(!data) return;
  const q = $('search').value.toLowerCase().trim();
  const rows = data.contributors.filter(c=>c.login.toLowerCase().includes(q));
  $('contributors').innerHTML = rows.map(c => `<tr><td class="user">${c.login}</td><td><span class="badge ${c.returned?'returned':'dropped'}">${c.returned?'RETURNED':'DROPPED'}</span></td><td>${fmtHours(c.firstResponseHours)}</td><td>${fmtHours(c.reviewHours)}</td><td>${fmtDays(c.mergeDays)}</td><td>${c.reviewRounds}</td><td class="result ${c.merged?'yes':'no'}">${c.merged?'Merged':'Not merged'}</td></tr>`).join('') || '<tr><td colspan="7" class="empty">No contributors found.</td></tr>';
}

async function loadDemo(){
  setLoading(true);
  const r = await fetch('/api/demo');
  const d = await r.json();
  render(d,'Demo Mode');
  $('loading').classList.add('hidden');
}

async function analyze(){
  const repo = $('repoInput').value.trim();
  if(!repo) return showError('Enter a GitHub repository like owner/repository.');
  setLoading(true);
  try {
    const r = await fetch(`/api/analyze?repo=${encodeURIComponent(repo)}`);
    const d = await r.json();
    if(!r.ok) throw new Error(d.error || 'Analysis failed.');
    render(d, `GitHub · ${repo}`);
    $('loading').classList.add('hidden');
  } catch(e) { showError(e.message); }
}

$('analyzeBtn').addEventListener('click', analyze);
$('demoBtn').addEventListener('click', loadDemo);
$('repoInput').addEventListener('keydown', e => { if(e.key==='Enter') analyze(); });
$('search').addEventListener('input', renderTable);
$('repoInput').value = DEFAULT_REPO;
loadDemo();
