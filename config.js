// Hinge Tracker - Environment & Backend Configuration
window.APP_CONFIG = {
  // Static ngrok HTTPS tunnel domain for remote mobile access via GitHub Pages
  API_BASE_URL: 'https://subplot-sarcastic-yesterday.ngrok-free.dev'
};

/**
 * Resolves the effective API base URL for network requests.
 * - If running on localhost or 127.0.0.1, routes to the local server directly ("").
 * - If running on GitHub Pages (or any remote origin), routes to the secure ngrok static domain.
 */
function getApiBaseUrl() {
  const host = window.location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || window.location.protocol === 'file:') {
    return '';
  }
  if (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) {
    return window.APP_CONFIG.API_BASE_URL.replace(/\/+$/, '');
  }
  return '';
}
