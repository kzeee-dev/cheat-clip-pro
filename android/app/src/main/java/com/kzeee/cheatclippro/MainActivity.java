package com.kzeee.cheatclippro;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.DownloadListener;
import android.webkit.WebView;
import android.widget.Toast;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        WebView webView = getBridge().getWebView();
        webView.setDownloadListener((url, userAgent, contentDisposition, mimeType, contentLength) -> {
            try {
                Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                browserIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

                // Keep the previous browser-based download flow: open the download URL in Chrome.
                browserIntent.setPackage("com.android.chrome");
                try {
                    startActivity(browserIntent);
                } catch (ActivityNotFoundException chromeNotInstalled) {
                    browserIntent.setPackage(null);
                    startActivity(browserIntent);
                }
            } catch (Exception error) {
                Toast.makeText(
                    this,
                    "Tidak bisa membuka tautan download: " + error.getMessage(),
                    Toast.LENGTH_LONG
                ).show();
            }
        });
    }
}
