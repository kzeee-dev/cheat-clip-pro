# API Contracts

This document must describe actual request/response models and routes.
Do not invent endpoints or schemas.

## Known router groups
- analyze
- cookies
- downloads
- media
- render
- system

## Known frontend API entry
- src/utils/api.ts

## Audit required
- Enumerate all registered routes from backend source.
- Record HTTP method, path, request schema, response schema and errors.
- Record streaming/SSE event formats.
- Record frontend callers and compatibility constraints.
- Record authentication, cookie and proxy behavior where applicable.

Status: PENDING SOURCE AUDIT.
