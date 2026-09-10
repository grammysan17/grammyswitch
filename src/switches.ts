export interface Switch {
  id: string;
  label: string;
  on: boolean;
}

/**
 * In-memory store of toggleable switches.
 *
 * This is intentionally simple (no persistence) so the app can be run and
 * demonstrated end to end without any external dependencies or secrets.
 */
export class SwitchBoard {
  private readonly switches = new Map<string, Switch>();

  constructor(initial: ReadonlyArray<Omit<Switch, 'on'> & { on?: boolean }> = []) {
    for (const item of initial) {
      this.switches.set(item.id, {
        id: item.id,
        label: item.label,
        on: item.on ?? false,
      });
    }
  }

  list(): Switch[] {
    return [...this.switches.values()];
  }

  get(id: string): Switch | undefined {
    return this.switches.get(id);
  }

  /**
   * Flip a single switch. Returns the updated switch, or undefined if the id
   * does not exist.
   */
  toggle(id: string): Switch | undefined {
    const current = this.switches.get(id);
    if (!current) {
      return undefined;
    }
    const updated: Switch = { ...current, on: !current.on };
    this.switches.set(id, updated);
    return updated;
  }

  /** Set every switch to the same state. Returns the full board. */
  setAll(on: boolean): Switch[] {
    for (const [id, current] of this.switches) {
      this.switches.set(id, { ...current, on });
    }
    return this.list();
  }

  /** Number of switches currently on. */
  countOn(): number {
    return this.list().filter((s) => s.on).length;
  }
}

export function createDefaultBoard(): SwitchBoard {
  return new SwitchBoard([
    { id: 'porch', label: 'Porch light' },
    { id: 'kitchen', label: 'Kitchen light', on: true },
    { id: 'garage', label: 'Garage door' },
    { id: 'sprinkler', label: 'Sprinkler' },
  ]);
}
