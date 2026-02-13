# Development Guide

## Deploying to GitHub Pages

The web app (Vite) is preconfigured with `base: '/yoot/'` for GitHub Pages.

### Setup (one-time)

1. Create a GitHub repo (e.g. `yoot`)
2. Add it as remote:
   ```bash
   git remote add origin git@github.com:<username>/yoot.git
   ```
3. Install the deploy tool:
   ```bash
   cd yoot-web
   pnpm add -D gh-pages
   ```

### Deploy

```bash
cd yoot-web
pnpm build
npx gh-pages -d dist
```

This pushes `dist/` to the `gh-pages` branch.

Then in GitHub repo **Settings > Pages**, set source to the `gh-pages` branch.

Your site will be at: `https://<username>.github.io/yoot/`
