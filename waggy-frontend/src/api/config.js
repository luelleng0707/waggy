/** Same-origin API base unless the portable server injects WAGGY_API_BASE_URL. */

export function getApiBaseUrl() {
  var configured = globalThis.__WAGGY_API_BASE_URL;
  if (configured) {
    return String(configured).replace(/\/$/, "");
  }
  return window.location.origin;
}

export function apiUrl(path) {
  var base = getApiBaseUrl();
  if (!path.startsWith("/")) {
    path = "/" + path;
  }
  return base + path;
}
