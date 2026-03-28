# GitCode API Specification (Issue Creation)

## Base URL

```
https://api.gitcode.com/api/v5
```

## Authentication

All requests require a `private-token` header:

```
private-token: <GITCODE_TOKEN>
```

Token needs `read_projects` + `write_issues` scopes. Store in `.env` as `GITCODE_TOKEN`.

## Create Issue

```
POST /repos/{owner}/{repo}/issues
Content-Type: application/json
```

Request body:
```json
{
  "access_token": "<token>",
  "repo": "<repo>",
  "title": "Issue title",
  "body": "Issue body in Markdown",
  "labels": "label1,label2,label3"
}
```

Response (201 Created):
```json
{
  "id": 12345,
  "number": "I123AB",
  "title": "Issue title",
  "state": "open",
  "html_url": "https://gitcode.com/mindspore/mindspore/issues/I123AB",
  "created_at": "2026-03-12T10:00:00+08:00"
}
```

## Error Responses

- `400`: Missing required fields or invalid payload
- `401`: Missing `private-token` header
- `403`: Invalid token or insufficient scopes (needs `write_issues`)
- `404`: Repository not found
- `422`: Validation error (e.g., title too long)

## Labels

Issue labels are passed as a comma-separated string. Pre-create these labels in the repo:
- `geo-improvement` — All GEO-generated issues
- `P0`, `P1`, `P2` — Severity levels
- `seo`, `content`, `documentation` — Category labels
