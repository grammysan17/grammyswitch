import express, { type Express } from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createDefaultBoard, SwitchBoard } from './switches.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export interface AppOptions {
  board?: SwitchBoard;
}

/**
 * Build the Express application. The board can be injected to make the API
 * easy to test in isolation.
 */
export function createApp(options: AppOptions = {}): Express {
  const board = options.board ?? createDefaultBoard();
  const app = express();

  app.use(express.json());

  app.get('/api/health', (_req, res) => {
    res.json({ status: 'ok' });
  });

  app.get('/api/switches', (_req, res) => {
    res.json({ switches: board.list(), on: board.countOn() });
  });

  app.post('/api/switches/:id/toggle', (req, res) => {
    const updated = board.toggle(req.params.id);
    if (!updated) {
      res.status(404).json({ error: `Unknown switch: ${req.params.id}` });
      return;
    }
    res.json({ switch: updated, on: board.countOn() });
  });

  app.post('/api/switches/all', (req, res) => {
    const on = Boolean(req.body?.on);
    const switches = board.setAll(on);
    res.json({ switches, on: board.countOn() });
  });

  // Serve the static frontend from /public.
  app.use(express.static(path.join(__dirname, '..', 'public')));

  return app;
}
