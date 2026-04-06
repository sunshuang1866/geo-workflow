# How to Obtain a ChatGPT Session Token

The `platform-chat` skill requires a valid `__Secure-next-auth.session-token` cookie from a logged-in ChatGPT session. Follow these steps to obtain it.

## Step-by-Step

### 1. Log in to ChatGPT in your local browser

Open a browser (Chrome, Firefox, Safari) and log in at [https://chatgpt.com](https://chatgpt.com).

### 2. Open Developer Tools

- **Chrome / Edge**: Press `F12` or right-click → Inspect → **Application** tab
- **Firefox**: Press `F12` → **Storage** tab
- **Safari**: Enable Develop menu in Settings → Develop → Show Web Inspector → **Storage** tab

### 3. Navigate to Cookies

In the DevTools panel:
- Chrome/Edge: Application → Storage → Cookies → `https://chatgpt.com`
- Firefox: Storage → Cookies → `https://chatgpt.com`

### 4. Find the Token

Look for the cookie named:
```
__Secure-next-auth.session-token
```

Click on it and copy the full **Value** field. It is a long JWT-like string (typically 500–2000+ characters).

### 5. Inject the Token

Run the inject script on the server:
```bash
python3 .claude/skills/platform-chat/scripts/inject-token.py \
  --token "<paste token here>" \
  --community MindSpore
```

The script will:
1. Save the token to `assessments/MindSpore/.chatgpt-session.json`
2. Launch a headless browser to verify the session is valid
3. Print `SESSION_VALID` on success or `SESSION_EXPIRED` on failure

### 6. Token Lifetime

ChatGPT session tokens typically expire after **30–90 days** of inactivity, or immediately after logout. If `verify-session.py` returns `SESSION_EXPIRED`, repeat steps 1–5 to obtain a fresh token.

## Security Note

The session file is saved as `.chatgpt-session.json` (dot-prefix). Ensure it is listed in `.gitignore` to prevent accidental commits:

```gitignore
assessments/**/.chatgpt-session.json
```
