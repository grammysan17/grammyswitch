const listEl = document.getElementById('switch-list');
const onCountEl = document.getElementById('on-count');
const totalCountEl = document.getElementById('total-count');

async function fetchState() {
  const res = await fetch('/api/switches');
  if (!res.ok) throw new Error(`Failed to load switches: ${res.status}`);
  return res.json();
}

async function toggle(id) {
  const res = await fetch(`/api/switches/${id}/toggle`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to toggle ${id}: ${res.status}`);
  return res.json();
}

async function setAll(on) {
  const res = await fetch('/api/switches/all', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ on }),
  });
  if (!res.ok) throw new Error(`Failed to set all: ${res.status}`);
  return res.json();
}

function render(state) {
  onCountEl.textContent = String(state.on);
  totalCountEl.textContent = String(state.switches.length);

  listEl.replaceChildren(
    ...state.switches.map((sw) => {
      const li = document.createElement('li');
      li.className = 'switch-row';

      const label = document.createElement('span');
      label.className = 'switch-row__label';
      label.textContent = sw.label;

      const button = document.createElement('button');
      button.className = 'toggle';
      button.type = 'button';
      button.setAttribute('aria-pressed', String(sw.on));
      button.setAttribute('aria-label', `Toggle ${sw.label}`);
      button.dataset.id = sw.id;

      const knob = document.createElement('span');
      knob.className = 'toggle__knob';
      button.appendChild(knob);

      button.addEventListener('click', async () => {
        const next = await toggle(sw.id);
        render(next);
      });

      li.append(label, button);
      return li;
    }),
  );
}

document.getElementById('all-on').addEventListener('click', async () => {
  render(await setAll(true));
});

document.getElementById('all-off').addEventListener('click', async () => {
  render(await setAll(false));
});

fetchState().then(render).catch(console.error);
