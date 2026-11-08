import { Capacitor } from '@capacitor/core';
import { apiUrl, resilientFetch } from './api';

/**
 * Download a Blob in the browser. Android WebView cannot pass blob: URLs to
 * DownloadManager, so native downloads are staged on the Termux backend and
 * then started from a real HTTP(S) URL.
 */
export function triggerBrowserDownload(blob: Blob, filename: string) {
  if (Capacitor.isNativePlatform()) {
    void (async () => {
      const safeFilename = filename || 'cheat_clip_download';
      const extension = safeFilename.match(/\\.[a-z0-9]{2,5}$/i)?.[0] || '.mp4';
      const title = safeFilename.slice(0, -extension.length) || 'download';
      const formData = new FormData();
      formData.append('file', blob, safeFilename);
      formData.append('title', title);

      const response = await resilientFetch(apiUrl('/api/save-client-download'), {
        method: 'POST',
        body: formData,
        credentials: 'include',
        maxRetries: 0,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.download_url) {
        throw new Error(data.detail || `Gagal menyiapkan download (HTTP ${response.status})`);
      }

      const downloadUrl = new URL(apiUrl(data.download_url), window.location.origin);
      if (downloadUrl.protocol !== 'http:' && downloadUrl.protocol !== 'https:') {
        throw new Error('Alamat download Android tidak valid.');
      }

      const link = document.createElement('a');
      link.href = downloadUrl.toString();
      link.download = safeFilename;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      link.remove();
    })().catch((error) => {
      console.error('Native blob download failed:', error);
      window.alert(error instanceof Error ? error.message : 'Gagal mengunduh file.');
    });
    return;
  }

  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}
