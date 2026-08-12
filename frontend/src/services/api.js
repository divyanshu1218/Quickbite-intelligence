const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchOverview() {
  const res = await fetch(`${API_BASE}/api/overview`);
  if (!res.ok) throw new Error('Failed to fetch overview data');
  return res.json();
}

export async function fetchSampleQuestions() {
  const res = await fetch(`${API_BASE}/api/sample-questions`);
  if (!res.ok) throw new Error('Failed to fetch sample questions');
  return res.json();
}

export async function submitQuestion(question) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error('Failed to process query');
  return res.json();
}

export async function fetchComparison(stores = null, months = 3) {
  const res = await fetch(`${API_BASE}/api/compare-stores`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stores, months }),
  });
  if (!res.ok) throw new Error('Failed to fetch store comparison');
  return res.json();
}

export async function fetchRecommendations(storeId, months = 3) {
  const res = await fetch(`${API_BASE}/api/recommendations/${storeId}?months=${months}`);
  if (!res.ok) throw new Error(`Failed to fetch recommendations for store ${storeId}`);
  return res.json();
}

export async function fetchNlToSql(question) {
  const res = await fetch(`${API_BASE}/api/nl-to-sql`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error('NL-to-SQL query failed');
  return res.json();
}

export async function fetchTimeMachine() {
  const res = await fetch(`${API_BASE}/api/time-machine/timeline`);
  if (!res.ok) throw new Error('Failed to fetch time machine timeline');
  return res.json();
}


export async function fetchProducts() {
  const res = await fetch(`${API_BASE}/api/products`);
  if (!res.ok) throw new Error('Failed to fetch products performance');
  return res.json();
}

export async function fetchChannels() {
  const res = await fetch(`${API_BASE}/api/channels`);
  if (!res.ok) throw new Error('Failed to fetch channels performance');
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}
