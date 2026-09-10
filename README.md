# grammyswitch

A tiny switch/toggle board web app used to bootstrap and demonstrate the
`grammyswitch` development environment. It has an Express + TypeScript backend
and a dependency-free static frontend, so it runs end to end with no external
services or secrets.

## Requirements

- Node.js >= 20 (developed against Node 22)
- npm (uses the committed `package-lock.json`)

## Getting started

```bash
npm ci            # install dependencies
npm run dev       # start the dev server with hot reload on http://localhost:3000
```

Then open http://localhost:3000 and toggle the switches.

## Scripts

| Command             | Description                                   |
| ------------------- | --------------------------------------------- |
| `npm run dev`       | Start the dev server (tsx watch) on port 3000 |
| `npm run build`     | Compile TypeScript to `dist/`                 |
| `npm start`         | Run the compiled server from `dist/`          |
| `npm run typecheck` | Type-check without emitting                   |
| `npm run lint`      | Lint with ESLint                              |
| `npm run format`    | Check formatting with Prettier                |
| `npm test`          | Run the Vitest suite                          |

## API

| Method | Path                       | Description                 |
| ------ | -------------------------- | --------------------------- |
| GET    | `/api/health`              | Health check                |
| GET    | `/api/switches`            | List switches and on-count  |
| POST   | `/api/switches/:id/toggle` | Toggle a single switch      |
| POST   | `/api/switches/all`        | Set all switches (`{ on }`) |

## Project layout

```
src/            Express app, server entry, and switch store
public/         Static frontend (HTML/CSS/JS)
test/           Vitest unit + API tests
.cursor/        Cloud Agent environment configuration
```
