# BIS SmartAssist — React (Vite) Version

Converted from the original single-file HTML preview (which used
`React.createElement` calls loaded via CDN `<script type="module">`)
into a standard Vite + React project with real `.jsx` files and JSX syntax.

## Structure

```
bis-smartassist/
├── index.html            # Vite entry HTML (loads Google Fonts + /src/main.jsx)
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx           # ReactDOM root render
    ├── App.jsx            # Main app: auth gate, layout, state, handlers
    ├── index.css          # All styles (extracted from the original <style> block)
    ├── components/
    │   ├── AuthScreen.jsx
    │   ├── Sidebar.jsx
    │   ├── Topbar.jsx
    │   ├── EmptyState.jsx
    │   ├── Thread.jsx
    │   ├── Composer.jsx
    │   └── BrandLogo.jsx
    └── utils/
        ├── logo.js         # BIS_LOGO_BASE64 constant
        └── bisAnswers.js   # getBISAnswer() + formatDateTime()
```

## Running it

```bash
cd bis-smartassist
npm install
npm run dev
```

Then open the printed local URL (usually `http://localhost:5173`).

## Notes on the conversion

- All `React.createElement(...)` calls were rewritten as JSX.
- Logic (state, handlers, `localStorage` persistence, the demo
  `getBISAnswer` knowledge base) is unchanged from the original.
- The app still uses `localStorage` for the demo login/session and
  saved conversations, exactly as it did in the original HTML file —
  if you plan to embed this component somewhere that disallows
  browser storage (e.g. Claude.ai artifacts), swap those calls for
  in-memory state instead.
- Demo login: `rahul@example.com` / `password123` (auto-seeded on
  first run), or use "Sign Up" to create a new local account.
