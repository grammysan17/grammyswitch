import { describe, expect, it } from 'vitest';
import { createDefaultBoard, SwitchBoard } from '../src/switches.js';

describe('SwitchBoard', () => {
  it('starts with the provided initial state', () => {
    const board = new SwitchBoard([
      { id: 'a', label: 'A' },
      { id: 'b', label: 'B', on: true },
    ]);

    expect(board.list()).toEqual([
      { id: 'a', label: 'A', on: false },
      { id: 'b', label: 'B', on: true },
    ]);
    expect(board.countOn()).toBe(1);
  });

  it('toggles a known switch', () => {
    const board = new SwitchBoard([{ id: 'a', label: 'A' }]);

    expect(board.toggle('a')).toEqual({ id: 'a', label: 'A', on: true });
    expect(board.toggle('a')).toEqual({ id: 'a', label: 'A', on: false });
  });

  it('returns undefined when toggling an unknown switch', () => {
    const board = new SwitchBoard([{ id: 'a', label: 'A' }]);
    expect(board.toggle('missing')).toBeUndefined();
  });

  it('sets every switch to the same state', () => {
    const board = createDefaultBoard();
    board.setAll(true);
    expect(board.countOn()).toBe(board.list().length);

    board.setAll(false);
    expect(board.countOn()).toBe(0);
  });
});
