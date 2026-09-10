import { describe, expect, it } from 'vitest';
import request from 'supertest';
import { createApp } from '../src/app.js';
import { SwitchBoard } from '../src/switches.js';

function appWithBoard() {
  const board = new SwitchBoard([
    { id: 'porch', label: 'Porch light' },
    { id: 'kitchen', label: 'Kitchen light', on: true },
  ]);
  return createApp({ board });
}

describe('API', () => {
  it('reports health', async () => {
    const res = await request(appWithBoard()).get('/api/health');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: 'ok' });
  });

  it('lists switches with the on count', async () => {
    const res = await request(appWithBoard()).get('/api/switches');
    expect(res.status).toBe(200);
    expect(res.body.on).toBe(1);
    expect(res.body.switches).toHaveLength(2);
  });

  it('toggles a switch', async () => {
    const app = appWithBoard();
    const res = await request(app).post('/api/switches/porch/toggle');
    expect(res.status).toBe(200);
    expect(res.body.switch).toEqual({ id: 'porch', label: 'Porch light', on: true });
    expect(res.body.on).toBe(2);
  });

  it('returns 404 for an unknown switch', async () => {
    const res = await request(appWithBoard()).post('/api/switches/nope/toggle');
    expect(res.status).toBe(404);
    expect(res.body.error).toContain('nope');
  });

  it('sets all switches at once', async () => {
    const app = appWithBoard();
    const res = await request(app).post('/api/switches/all').send({ on: false });
    expect(res.status).toBe(200);
    expect(res.body.on).toBe(0);
  });

  it('serves the frontend', async () => {
    const res = await request(appWithBoard()).get('/');
    expect(res.status).toBe(200);
    expect(res.text).toContain('grammyswitch');
  });
});
