/**
 * Resilient API client for Cheat Clip Pro.
 * Supports Android local backend and normal web development.
 */

export interface ResilientFetchOptions extends RequestInit {
  maxRetries?: number;
  retryDelay?: number;
  silent?: boolean;
}

import { Capacitor } from '@capacitor/core';

// In the installed Android app, relative /api requests target the WebView origin,
// not the Python server running in Termux. Use the device loopback explicitly.
const DEFAULT_NATIVE_API_BASE_URL = Capacitor.isNativePlatform()
  ? 'http://localhost:8000'
  : '';

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || DEFAULT_NATIVE_API_BASE_URL
).replace(/\/+$/, '');

export function apiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;

  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  return API_BASE_URL
    ? `${API_BASE_URL}${normalizedPath}`
    : normalizedPath;
}

export async function resilientFetch(
  input: RequestInfo | URL,
  options: ResilientFetchOptions = {}
): Promise<Response> {
  const {
    maxRetries = 4,
    retryDelay = 800,
    silent = false,
    ...fetchInit
  } = options;

  const resolvedInput =
    typeof input === 'string'
      ? apiUrl(input)
      : input instanceof URL
        ? apiUrl(input.toString())
        : input;

  let lastError: any = null;
  let lastResponse: Response | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(resolvedInput, fetchInit);

      if (
        response.status !== 503 &&
        response.status !== 502 &&
        response.status !== 504
      ) {
        return response;
      }

      lastResponse = response;

      if (!silent) {
        console.warn(
          `[resilientFetch] Backend responded with HTTP ${response.status} for ${String(resolvedInput)} (attempt ${attempt + 1}/${maxRetries + 1}). Retrying...`
        );
      }
    } catch (err: any) {
      lastError = err;

      if (!silent) {
        console.warn(
          `[resilientFetch] Network error for ${String(resolvedInput)} (attempt ${attempt + 1}/${maxRetries + 1}):`,
          err?.message || err
        );
      }
    }

    if (attempt < maxRetries) {
      const delay = Math.round(
        retryDelay * Math.pow(1.5, attempt)
      );
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  if (lastResponse) return lastResponse;

  throw lastError || new Error(
    `Failed to fetch ${String(resolvedInput)} after ${maxRetries + 1} attempts`
  );
}
