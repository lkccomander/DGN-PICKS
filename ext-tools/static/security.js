function desktopFetch(path, init = {}) {
  const url = new URL(path, window.location.href);
  if (url.origin !== window.location.origin || !url.pathname.startsWith('/api/')) throw new Error('Desktop API requests must use the current origin');
  const method = (init.method || 'GET').toUpperCase();
  const mutation = !['GET', 'HEAD', 'OPTIONS'].includes(method);
  const headers = new Headers(init.headers);
  if (mutation) {
    const token = document.querySelector('meta[name="dgn-csrf-token"]')?.content;
    if (!token) throw new Error('Desktop request token is missing');
    headers.set('X-DGN-CSRF', token);
    headers.set('Content-Type', 'application/json');
  }
  return fetch(url, { ...init, method, headers, credentials: 'same-origin', redirect: 'error', ...(mutation && init.body == null ? { body: '{}' } : {}) });
}
