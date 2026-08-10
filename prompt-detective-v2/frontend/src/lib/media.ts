export const resolveBackendAssetUrl = (url?: string | null): string | undefined => {
  if (!url) {
    return undefined;
  }

  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url;
  }

  const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/?api\/v1\/?$/, '');
  const normalizedPath = url.startsWith('/') ? url : `/${url}`;
  const base = apiBase.endsWith('/') ? apiBase.slice(0, -1) : apiBase;

  return `${base}${normalizedPath}`;
};
