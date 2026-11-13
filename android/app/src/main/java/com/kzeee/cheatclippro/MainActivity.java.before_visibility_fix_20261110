package com.kzeee.cheatclippro;

import android.app.DownloadManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.webkit.CookieManager;
import android.webkit.DownloadListener;
import android.webkit.URLUtil;
import android.webkit.WebView;
import android.widget.Toast;

import androidx.core.content.ContextCompat;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    private static final String TAG = "CheatClipDownload";
    private static final String PREFS_NAME = "cheat_clip_downloads";
    private static final String KEY_LAST_DOWNLOAD_ID = "last_download_id";

    private DownloadManager downloadManager;
    private boolean receiverRegistered = false;

    private final BroadcastReceiver downloadReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (DownloadManager.ACTION_DOWNLOAD_COMPLETE.equals(intent.getAction())) {
                long completedId = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1L);
                if (completedId != -1L) {
                    inspectDownload(completedId);
                }
            }
        }
    };

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        downloadManager = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
        IntentFilter filter = new IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE);
        ContextCompat.registerReceiver(
            this,
            downloadReceiver,
            filter,
            ContextCompat.RECEIVER_EXPORTED
        );
        receiverRegistered = true;

        WebView webView = getBridge().getWebView();
        webView.setDownloadListener((url, userAgent, contentDisposition, mimeType, contentLength) -> {
            try {
                String fileName = URLUtil.guessFileName(url, contentDisposition, mimeType);
                if (fileName == null || fileName.trim().isEmpty()) {
                    fileName = "cheat_clip_download";
                }

                DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
                request.setTitle(fileName);
                request.setDescription("Mengunduh file dari Cheat Clip Pro");
                request.setMimeType(mimeType != null ? mimeType : "application/octet-stream");
                request.setNotificationVisibility(
                    DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED
                );
                request.setAllowedOverMetered(true);
                request.setAllowedOverRoaming(true);
                request.setDestinationInExternalPublicDir(
                    Environment.DIRECTORY_DOWNLOADS,
                    fileName
                );

                String cookie = CookieManager.getInstance().getCookie(url);
                if (cookie != null && !cookie.isEmpty()) {
                    request.addRequestHeader("Cookie", cookie);
                }
                if (userAgent != null && !userAgent.isEmpty()) {
                    request.addRequestHeader("User-Agent", userAgent);
                }

                if (downloadManager == null) {
                    Toast.makeText(this, "Layanan download Android tidak tersedia", Toast.LENGTH_LONG).show();
                    return;
                }

                long downloadId = downloadManager.enqueue(request);
                getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                    .edit()
                    .putLong(KEY_LAST_DOWNLOAD_ID, downloadId)
                    .apply();

                Log.i(TAG, "Download queued. id=" + downloadId + ", url=" + url
                    + ", expectedBytes=" + contentLength);
                Toast.makeText(this, "Download dimulai: " + fileName, Toast.LENGTH_SHORT).show();
            } catch (Exception error) {
                Log.e(TAG, "Could not enqueue download", error);
                Toast.makeText(
                    this,
                    "Gagal memulai download: " + error.getMessage(),
                    Toast.LENGTH_LONG
                ).show();
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        long lastId = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
            .getLong(KEY_LAST_DOWNLOAD_ID, -1L);
        if (lastId != -1L) {
            inspectDownload(lastId);
        }
    }

    private void inspectDownload(long downloadId) {
        if (downloadManager == null) return;

        Cursor cursor = null;
        try {
            DownloadManager.Query query = new DownloadManager.Query().setFilterById(downloadId);
            cursor = downloadManager.query(query);

            if (cursor == null || !cursor.moveToFirst()) {
                Log.w(TAG, "No DownloadManager record found for id=" + downloadId);
                return;
            }

            int statusIndex = cursor.getColumnIndex(DownloadManager.COLUMN_STATUS);
            int reasonIndex = cursor.getColumnIndex(DownloadManager.COLUMN_REASON);
            int uriIndex = cursor.getColumnIndex(DownloadManager.COLUMN_LOCAL_URI);
            int bytesIndex = cursor.getColumnIndex(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR);
            int totalIndex = cursor.getColumnIndex(DownloadManager.COLUMN_TOTAL_SIZE_BYTES);

            int status = statusIndex >= 0 ? cursor.getInt(statusIndex) : -1;
            int reason = reasonIndex >= 0 ? cursor.getInt(reasonIndex) : 0;
            long downloaded = bytesIndex >= 0 ? cursor.getLong(bytesIndex) : -1L;
            long total = totalIndex >= 0 ? cursor.getLong(totalIndex) : -1L;
            String localUri = uriIndex >= 0 ? cursor.getString(uriIndex) : null;

            Log.i(TAG, "Download status. id=" + downloadId + ", status=" + status
                + ", reason=" + reason + ", bytes=" + downloaded + "/" + total
                + ", localUri=" + localUri);

            if (status == DownloadManager.STATUS_SUCCESSFUL) {
                clearLastDownloadId(downloadId);
                Toast.makeText(
                    this,
                    "Download selesai. Cek folder Download.",
                    Toast.LENGTH_LONG
                ).show();
            } else if (status == DownloadManager.STATUS_FAILED) {
                clearLastDownloadId(downloadId);
                String detail = describeFailure(reason);
                Log.e(TAG, "Download failed. id=" + downloadId + ", " + detail);
                Toast.makeText(
                    this,
                    "Download gagal: " + detail,
                    Toast.LENGTH_LONG
                ).show();
            }
        } catch (Exception error) {
            Log.e(TAG, "Failed to inspect DownloadManager status for id=" + downloadId, error);
        } finally {
            if (cursor != null) cursor.close();
        }
    }

    private void clearLastDownloadId(long downloadId) {
        getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
            .edit()
            .remove(KEY_LAST_DOWNLOAD_ID)
            .apply();
    }

    private String describeFailure(int reason) {
        switch (reason) {
            case DownloadManager.ERROR_CANNOT_RESUME:
                return "unduhan tidak bisa dilanjutkan (ERROR_CANNOT_RESUME)";
            case DownloadManager.ERROR_DEVICE_NOT_FOUND:
                return "penyimpanan tidak ditemukan (ERROR_DEVICE_NOT_FOUND)";
            case DownloadManager.ERROR_FILE_ALREADY_EXISTS:
                return "file sudah ada (ERROR_FILE_ALREADY_EXISTS)";
            case DownloadManager.ERROR_FILE_ERROR:
                return "kesalahan penyimpanan (ERROR_FILE_ERROR)";
            case DownloadManager.ERROR_HTTP_DATA_ERROR:
                return "data HTTP tidak valid (ERROR_HTTP_DATA_ERROR)";
            case DownloadManager.ERROR_INSUFFICIENT_SPACE:
                return "ruang penyimpanan tidak cukup (ERROR_INSUFFICIENT_SPACE)";
            case DownloadManager.ERROR_TOO_MANY_REDIRECTS:
                return "terlalu banyak pengalihan (ERROR_TOO_MANY_REDIRECTS)";
            case DownloadManager.ERROR_UNHANDLED_HTTP_CODE:
                return "server mengembalikan kode HTTP yang tidak didukung";
            case DownloadManager.ERROR_UNKNOWN:
                return "kesalahan tidak diketahui (ERROR_UNKNOWN)";
            default:
                if (reason >= 400) return "HTTP " + reason;
                return "kode error " + reason;
        }
    }

    @Override
    protected void onDestroy() {
        if (receiverRegistered) {
            unregisterReceiver(downloadReceiver);
            receiverRegistered = false;
        }
        super.onDestroy();
    }
}
