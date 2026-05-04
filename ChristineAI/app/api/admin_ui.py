# ruff: noqa: E501
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


ADMIN_HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>ChristineAI Admin</title>
  <style>
    :root {
      --SmartThemeBodyColor: rgb(220, 220, 210);
      --SmartThemeEmColor: rgb(145, 145, 145);
      --SmartThemeBlurTintColor: rgba(23, 23, 23, 1);
      --SmartThemeChatTintColor: rgba(23, 23, 23, 1);
      --SmartThemeBorderColor: rgba(85, 85, 85, 0.9);
      --SmartThemeBlurStrength: 10px;
      --black50a: rgba(0, 0, 0, 0.5);
      --white30a: rgba(255, 255, 255, 0.3);
      --white20a: rgba(255, 255, 255, 0.2);
      --grey7070a: rgba(175, 175, 175, 0.7);
      --mainFontSize: 15px;
      --mainFontFamily: \"Noto Sans\", \"Segoe UI\", sans-serif;
      --monoFontFamily: \"Noto Sans Mono\", \"Consolas\", monospace;
      --animation-duration-2x: 240ms;
      --animation-duration-3x: 360ms;
      --topBarIconSize: 30px;
      --topBarBlockSize: 44px;
      --okGreen70a: rgba(0, 100, 0, 0.7);
      --crimson70a: rgba(100, 0, 0, 0.8);
    }

    * {
      box-sizing: border-box;
      text-shadow: 0 0 1px var(--black50a);
    }

    body {
      margin: 0;
      background: radial-gradient(circle at top right, #3b3b3b 0%, var(--SmartThemeBlurTintColor) 45%, #121212 100%);
      color: var(--SmartThemeBodyColor);
      font-family: var(--mainFontFamily);
      font-size: var(--mainFontSize);
      min-height: 100vh;
      overflow-x: hidden;
    }

    #top-settings-holder {
      display: flex;
      margin: 0 auto;
      height: var(--topBarBlockSize);
      justify-content: center;
      z-index: 200;
      position: sticky;
      top: 0;
      width: min(1300px, 96vw);
      background-color: color-mix(in srgb, var(--SmartThemeBlurTintColor) 85%, transparent);
      backdrop-filter: blur(var(--SmartThemeBlurStrength));
      border-bottom: 1px solid var(--SmartThemeBorderColor);
      border-radius: 0 0 10px 10px;
    }

    .drawer {
      align-items: center;
      justify-content: center;
      display: flex;
      width: 100%;
      gap: 8px;
      padding: 0 8px;
    }

    .drawer-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 14px;
      padding: 6px 10px;
      border-radius: 6px;
      border: 1px solid var(--SmartThemeBorderColor);
      background: var(--SmartThemeBlurTintColor);
      color: var(--SmartThemeBodyColor);
      transition: all var(--animation-duration-2x);
    }

    .drawer-icon.closedIcon {
      opacity: 0.6;
    }

    .drawer-icon.closedIcon:hover,
    .drawer-icon.active {
      opacity: 1;
      background: var(--white20a);
    }

    .wrap {
      width: min(1300px, 96vw);
      margin: 14px auto 24px;
      display: grid;
      gap: 12px;
    }

    .drawer-content {
      background-color: color-mix(in srgb, var(--SmartThemeBlurTintColor) 92%, transparent);
      color: var(--SmartThemeBodyColor);
      border-radius: 10px;
      padding: 10px;
      border: 1px solid var(--SmartThemeBorderColor);
      backdrop-filter: blur(var(--SmartThemeBlurStrength));
    }

    .panel {
      display: none;
      gap: 10px;
      grid-template-columns: repeat(12, 1fr);
    }

    .panel.active {
      display: grid;
    }

    .card {
      border: 1px solid var(--SmartThemeBorderColor);
      background: color-mix(in srgb, var(--SmartThemeChatTintColor) 82%, transparent);
      border-radius: 10px;
      padding: 10px;
      grid-column: span 12;
      min-width: 0;
    }

    .card.half { grid-column: span 6; }
    .card.third { grid-column: span 4; }

    .muted {
      color: var(--SmartThemeEmColor);
      font-size: 12px;
      line-height: 1.4;
    }

    .menu_button {
      color: var(--SmartThemeBodyColor);
      background-color: var(--SmartThemeBlurTintColor);
      border: 1px solid var(--SmartThemeBorderColor);
      border-radius: 5px;
      padding: 6px 10px;
      cursor: pointer;
      transition: var(--animation-duration-2x);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      min-height: 34px;
    }

    .menu_button:hover {
      background-color: var(--white30a);
    }

    .menu_button.warn {
      background: var(--crimson70a);
    }

    .menu_button.ok {
      background: var(--okGreen70a);
    }

    input, textarea, select {
      width: 100%;
      background: rgba(0, 0, 0, 0.3);
      color: var(--SmartThemeBodyColor);
      border: 1px solid var(--SmartThemeBorderColor);
      border-radius: 6px;
      padding: 8px;
      font: inherit;
    }

    textarea {
      resize: vertical;
      min-height: 90px;
      font-family: var(--monoFontFamily);
      font-size: 13px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }

    th, td {
      border-bottom: 1px solid var(--SmartThemeBorderColor);
      text-align: left;
      padding: 6px;
      vertical-align: top;
    }

    .pill {
      display: inline-block;
      padding: 3px 7px;
      border-radius: 999px;
      border: 1px solid var(--SmartThemeBorderColor);
      background: rgba(0, 0, 0, 0.35);
      font-size: 12px;
    }

    .ok { color: #9dff9d; }
    .err { color: #ff8f8f; }

    pre {
      white-space: pre-wrap;
      word-break: break-word;
      background: rgba(0, 0, 0, 0.35);
      border: 1px solid var(--SmartThemeBorderColor);
      border-radius: 8px;
      padding: 8px;
      max-height: 340px;
      overflow: auto;
      margin: 0;
      font-family: var(--monoFontFamily);
      font-size: 12px;
    }

    .row {
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 8px;
      align-items: end;
    }

    .span-12 { grid-column: span 12; }
    .span-6 { grid-column: span 6; }
    .span-4 { grid-column: span 4; }
    .span-3 { grid-column: span 3; }
    .span-2 { grid-column: span 2; }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }

    .stack {
      display: grid;
      gap: 8px;
    }

    @media (max-width: 980px) {
      .card.half, .card.third,
      .span-6, .span-4, .span-3, .span-2 {
        grid-column: span 12;
      }
      #top-settings-holder {
        position: static;
        border-radius: 0;
        width: 100%;
      }
      .wrap { width: 100%; padding: 0 8px; }
      .drawer { overflow-x: auto; justify-content: flex-start; }
    }
  </style>
</head>
<body>
  <div id=\"top-settings-holder\">
    <div class=\"drawer\" id=\"tabs\">
      <button class=\"drawer-icon closedIcon active\" data-tab=\"overview\">Overview</button>
      <button class=\"drawer-icon closedIcon\" data-tab=\"users\">Users</button>
      <button class=\"drawer-icon closedIcon\" data-tab=\"assistants\">Assistants</button>
      <button class=\"drawer-icon closedIcon\" data-tab=\"devices\">Devices</button>
      <button class=\"drawer-icon closedIcon\" data-tab=\"tests\">Tests/Probe</button>
      <button class=\"drawer-icon closedIcon\" data-tab=\"logs\">Logs</button>
    </div>
  </div>

  <div class=\"wrap\">
    <section class=\"drawer-content\">
      <div class=\"row\">
        <div class=\"span-3\"><input id=\"email\" placeholder=\"Email\" /></div>
        <div class=\"span-3\"><input id=\"password\" type=\"password\" placeholder=\"Password\" /></div>
        <div class=\"span-2\"><input id=\"adminKey\" type=\"password\" placeholder=\"X-Admin-Key\" /></div>
        <div class=\"span-4 toolbar\">
          <button class=\"menu_button ok\" onclick=\"login()\">Login</button>
          <button class=\"menu_button\" onclick=\"refreshAll()\">Refresh</button>
          <button class=\"menu_button warn\" onclick=\"logout()\">Logout</button>
          <span id=\"authStatus\" class=\"pill\">Not authenticated</span>
        </div>
      </div>
      <div class=\"muted\" style=\"margin-top:8px;\">UI layer imported in SillyTavern-style drawer layout and simplified for ChristineAI admin operations.</div>
    </section>

    <section id=\"panel-overview\" class=\"panel active\">
      <article class=\"card half\">
        <h3>Service Overview</h3>
        <pre id=\"overview\">No data</pre>
      </article>
      <article class=\"card half\">
        <h3>Runtime</h3>
        <pre id=\"runtime\">No data</pre>
      </article>
    </section>

    <section id=\"panel-users\" class=\"panel\">
      <article class=\"card\">
        <div class=\"toolbar\" style=\"justify-content:space-between;\">
          <h3 style=\"margin:0;\">Users</h3>
          <div class=\"toolbar\">
            <button class=\"menu_button\" onclick=\"loadUsers()\">Reload Users</button>
            <span class=\"pill\" id=\"scopeBadge\">Scope: current user</span>
          </div>
        </div>
        <div id=\"usersTable\" style=\"margin-top:8px;\">No data</div>
      </article>
    </section>

    <section id=\"panel-assistants\" class=\"panel\">
      <article class=\"card\">
        <div class=\"toolbar\" style=\"justify-content:space-between;\">
          <h3 style=\"margin:0;\">Assistants / Personality / LLM</h3>
          <div class=\"toolbar\">
            <select id=\"assistantUserFilter\" style=\"min-width:260px\"></select>
            <button class=\"menu_button\" onclick=\"loadAssistants()\">Reload</button>
          </div>
        </div>
        <div id=\"assistantCreate\" class=\"stack\" style=\"margin-top:10px;\"></div>
        <div id=\"assistantsTable\" style=\"margin-top:10px;\">No data</div>
      </article>
    </section>

    <section id=\"panel-devices\" class=\"panel\">
      <article class=\"card\">
        <div class=\"toolbar\" style=\"justify-content:space-between;\">
          <h3 style=\"margin:0;\">Devices</h3>
          <div class=\"toolbar\">
            <select id=\"deviceUserFilter\" style=\"min-width:260px\"></select>
            <button class=\"menu_button\" onclick=\"loadDevices()\">Reload</button>
          </div>
        </div>
        <div id=\"deviceCreate\" class=\"stack\" style=\"margin-top:10px;\"></div>
        <div id=\"devicesTable\" style=\"margin-top:10px;\">No data</div>
      </article>
    </section>

    <section id=\"panel-tests\" class=\"panel\">
      <article class=\"card third\">
        <h3>Provider Probe</h3>
        <div class=\"stack\">
          <input id=\"probeBackend\" value=\"mock\" placeholder=\"backend\" />
          <input id=\"probeModel\" value=\"gpt-4o-mini\" placeholder=\"model\" />
          <textarea id=\"probePrompt\" placeholder=\"Prompt\"></textarea>
          <button class=\"menu_button\" onclick=\"runProbe()\">Run Probe</button>
          <pre id=\"probeResult\">No data</pre>
        </div>
      </article>
      <article class=\"card third\">
        <h3>Device Session Debug</h3>
        <div class=\"stack\">
          <select id=\"testDevice\"></select>
          <button class=\"menu_button\" onclick=\"loadSession()\">Load Session</button>
          <pre id=\"sessionResult\">No data</pre>
        </div>
      </article>
      <article class=\"card third\">
        <h3>Test Chat</h3>
        <div class=\"stack\">
          <textarea id=\"testMessage\" placeholder=\"Message\"></textarea>
          <button class=\"menu_button\" onclick=\"sendTestChat()\">Send</button>
          <pre id=\"testChatResult\">No data</pre>
        </div>
      </article>
    </section>

    <section id=\"panel-logs\" class=\"panel\">
      <article class=\"card\">
        <div class=\"toolbar\" style=\"justify-content:space-between;\">
          <h3 style=\"margin:0;\">Chat Turns</h3>
          <div class=\"toolbar\">
            <select id=\"logUserFilter\" style=\"min-width:260px\"></select>
            <select id=\"logStatus\">
              <option value=\"\">all statuses</option>
              <option value=\"ok\">ok</option>
              <option value=\"error\">error</option>
            </select>
            <input id=\"logLimit\" type=\"number\" value=\"30\" min=\"1\" max=\"500\" style=\"max-width:92px\" />
            <button class=\"menu_button\" onclick=\"loadChatTurns()\">Reload Logs</button>
          </div>
        </div>
        <div id=\"turnsTable\" style=\"margin-top:8px;\">No data</div>
      </article>
    </section>
  </div>

  <script>
    const API = '/api/v1';
    const tokenKey = 'christine_admin_token';
    const adminKeyStore = 'christine_admin_key';

    const state = {
      token: localStorage.getItem(tokenKey) || '',
      adminKey: localStorage.getItem(adminKeyStore) || '',
      globalAdmin: false,
      users: [],
      assistants: [],
      devices: [],
      selectedUserId: '',
      me: null,
    };

    const el = (id) => document.getElementById(id);

    el('adminKey').value = state.adminKey;

    function esc(raw) {
      return String(raw ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
    }

    function authHeaders(withJson = true) {
      const h = {};
      if (state.token) h['Authorization'] = 'Bearer ' + state.token;
      if (state.adminKey) h['X-Admin-Key'] = state.adminKey;
      if (withJson) h['Content-Type'] = 'application/json';
      return h;
    }

    function setStatus(text, ok = true) {
      const node = el('authStatus');
      node.textContent = text;
      node.className = 'pill ' + (ok ? 'ok' : 'err');
    }

    async function api(path, options = {}) {
      const res = await fetch(API + path, options);
      const text = await res.text();
      let body = text;
      try { body = JSON.parse(text); } catch (_) {}
      if (!res.ok) {
        const detail = typeof body === 'string' ? body : (body.detail || JSON.stringify(body));
        throw new Error(detail);
      }
      return body;
    }

    function selectedScopedUserId() {
      return state.globalAdmin ? (state.selectedUserId || '') : '';
    }

    function ensureUserScopeLabel() {
      const badge = el('scopeBadge');
      if (!badge) return;
      if (!state.globalAdmin) {
        badge.textContent = 'Scope: current user';
      } else if (!state.selectedUserId) {
        badge.textContent = 'Scope: all users';
      } else {
        const user = state.users.find((x) => x.id === state.selectedUserId);
        badge.textContent = 'Scope: ' + (user ? user.email : state.selectedUserId);
      }
    }

    function bindTabs() {
      document.querySelectorAll('#tabs [data-tab]').forEach((button) => {
        button.addEventListener('click', () => {
          document.querySelectorAll('#tabs [data-tab]').forEach((x) => x.classList.remove('active'));
          button.classList.add('active');
          const tab = button.getAttribute('data-tab');
          document.querySelectorAll('.panel').forEach((panel) => panel.classList.remove('active'));
          const target = el('panel-' + tab);
          if (target) target.classList.add('active');
        });
      });
    }

    function logout() {
      state.token = '';
      state.globalAdmin = false;
      localStorage.removeItem(tokenKey);
      setStatus('Logged out', true);
      ensureUserScopeLabel();
    }

    async function login() {
      try {
        const email = el('email').value.trim();
        const password = el('password').value;
        state.adminKey = el('adminKey').value.trim();
        localStorage.setItem(adminKeyStore, state.adminKey);

        const out = await api('/auth/login', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ email, password }),
        });
        state.token = out.access_token;
        localStorage.setItem(tokenKey, state.token);
        await refreshAll();
      } catch (e) {
        setStatus('Login failed: ' + e.message, false);
      }
    }

    async function detectGlobalAdmin() {
      try {
        await api('/admin/users', { headers: authHeaders(false) });
        return true;
      } catch (_) {
        return false;
      }
    }

    function renderUserSelectors() {
      const options = ['<option value="">All users</option>'].concat(
        state.users.map((u) => `<option value="${u.id}">${esc(u.email)} (${esc(u.plan)})</option>`)
      );
      const perUserOptions = ['<option value="">Current user</option>'].concat(
        state.users.map((u) => `<option value="${u.id}">${esc(u.email)} (${esc(u.plan)})</option>`)
      );

      ['assistantUserFilter', 'deviceUserFilter', 'logUserFilter'].forEach((id) => {
        const node = el(id);
        if (!node) return;
        node.innerHTML = state.globalAdmin ? options.join('') : '<option value="">Current user</option>';
        node.value = state.selectedUserId;
        node.disabled = !state.globalAdmin;
        node.onchange = () => {
          state.selectedUserId = node.value;
          renderUserSelectors();
          ensureUserScopeLabel();
          refreshDataOnly();
        };
      });

      const usersTab = el('panel-users');
      usersTab.style.display = state.globalAdmin ? 'grid' : 'none';

      if (!state.globalAdmin) {
        state.selectedUserId = '';
      }

      if (state.globalAdmin) {
        const defaults = [
          ['assistantUserFilter', state.selectedUserId],
          ['deviceUserFilter', state.selectedUserId],
          ['logUserFilter', state.selectedUserId],
        ];
        defaults.forEach(([id, value]) => {
          const node = el(id);
          if (node) node.value = value;
        });
      }

      ensureUserScopeLabel();
    }

    async function refreshAll() {
      try {
        if (!state.token) {
          setStatus('Token missing', false);
          return;
        }

        state.adminKey = el('adminKey').value.trim();
        localStorage.setItem(adminKeyStore, state.adminKey);

        state.me = await api('/auth/me', { headers: authHeaders(false) });
        state.globalAdmin = await detectGlobalAdmin();

        setStatus(
          `Authenticated as ${state.me.email}${state.globalAdmin ? ' (global admin)' : ''}`,
          true,
        );

        if (state.globalAdmin) {
          await loadUsers();
        } else {
          state.users = [];
          renderUserSelectors();
        }

        await refreshDataOnly();
      } catch (e) {
        setStatus('Refresh failed: ' + e.message, false);
      }
    }

    async function refreshDataOnly() {
      renderUserSelectors();
      await Promise.all([
        loadOverview(),
        loadAssistants(),
        loadDevices(),
        loadChatTurns(),
      ]);
      await syncTestDevices();
    }

    async function loadOverview() {
      const data = await api('/admin/overview', { headers: authHeaders(false) });
      el('overview').textContent = JSON.stringify({
        users: data.users,
        assistants: data.assistants,
        devices: data.devices,
        chat_turns_24h: data.chat_turns_24h,
        errors_24h: data.errors_24h,
      }, null, 2);
      el('runtime').textContent = JSON.stringify(data.runtime || {}, null, 2);
    }

    async function loadUsers() {
      if (!state.globalAdmin) {
        el('usersTable').innerHTML = '<div class="muted">Global mode disabled (set valid X-Admin-Key).</div>';
        return;
      }

      state.users = await api('/admin/users', { headers: authHeaders(false) });
      renderUserSelectors();

      const rows = state.users.map((u) => `
        <tr>
          <td>${esc(u.email)}<div class="muted">${u.id}</div></td>
          <td><input id="plan_${u.id}" value="${esc(u.plan)}" /></td>
          <td>${u.assistants}</td>
          <td>${u.devices}</td>
          <td>${u.chat_turns_24h}</td>
          <td>${u.last_seen || '-'}</td>
          <td>
            <div class="stack">
              <input id="pwd_${u.id}" type="password" placeholder="new password (optional)" />
              <div class="toolbar">
                <button class="menu_button" onclick="saveUser('${u.id}')">Save</button>
                <button class="menu_button" onclick="selectUser('${u.id}')">Scope</button>
              </div>
            </div>
          </td>
        </tr>
      `).join('');

      el('usersTable').innerHTML = `
        <table>
          <thead><tr><th>User</th><th>Plan</th><th>Assistants</th><th>Devices</th><th>Turns 24h</th><th>Last seen</th><th>Actions</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    function selectUser(userId) {
      state.selectedUserId = userId || '';
      renderUserSelectors();
      refreshDataOnly();
    }

    async function saveUser(userId) {
      const payload = {
        plan: el('plan_' + userId).value.trim(),
      };
      const pwd = el('pwd_' + userId).value;
      if (pwd.trim()) payload.password = pwd;
      await api('/admin/users/' + userId, {
        method: 'PATCH',
        headers: authHeaders(),
        body: JSON.stringify(payload),
      });
      await loadUsers();
    }

    function userQuery() {
      const userId = selectedScopedUserId();
      return userId ? ('?user_id=' + encodeURIComponent(userId)) : '';
    }

    async function loadAssistants() {
      const rows = await api('/admin/assistants/llm' + userQuery(), { headers: authHeaders(false) });
      state.assistants = rows;

      const tableRows = rows.map((a, i) => `
        <tr>
          <td>${esc(a.name)}<div class="muted">${a.id}<br>${a.user_id}</div></td>
          <td><input id="ab_${i}" value="${esc(a.llm_backend)}" /></td>
          <td><input id="am_${i}" value="${esc(a.llm_model)}" /></td>
          <td><textarea id="ao_${i}">${esc(JSON.stringify(a.llm_overrides || {}, null, 2))}</textarea></td>
          <td><textarea id="ap_${i}">${esc(JSON.stringify(a.personality || {}, null, 2))}</textarea></td>
          <td>
            <div class="stack">
              <button class="menu_button" onclick="saveAssistantLlm('${a.id}', ${i})">Save LLM</button>
              <button class="menu_button" onclick="saveAssistantPersonality('${a.id}', ${i})">Save Personality</button>
            </div>
          </td>
        </tr>
      `).join('');

      el('assistantsTable').innerHTML = rows.length
        ? `<table><thead><tr><th>Assistant</th><th>Backend</th><th>Model</th><th>Overrides JSON</th><th>Personality JSON</th><th>Actions</th></tr></thead><tbody>${tableRows}</tbody></table>`
        : '<div class="muted">No assistants</div>';

      renderAssistantCreate();
      renderDevicesTable();
      await syncTestDevices();
    }

    function renderAssistantCreate() {
      const box = el('assistantCreate');
      if (!state.globalAdmin) {
        box.innerHTML = '';
        return;
      }

      const selected = state.selectedUserId || '';
      box.innerHTML = `
        <div class="row">
          <div class="span-3"><input id="newAssistantName" placeholder="Assistant name" /></div>
          <div class="span-3"><input id="newAssistantBackend" value="mock" placeholder="backend" /></div>
          <div class="span-3"><input id="newAssistantModel" value="gpt-4o-mini" placeholder="model" /></div>
          <div class="span-3"><button class="menu_button" onclick="createAssistantForUser()">Create Assistant For Selected User</button></div>
          <div class="span-12 muted">Selected user id: ${selected || 'none (pick in user filters)'}</div>
        </div>
      `;
    }

    async function createAssistantForUser() {
      if (!state.globalAdmin || !state.selectedUserId) {
        alert('Select a user in scope first.');
        return;
      }
      await api('/admin/users/' + state.selectedUserId + '/assistants', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({
          name: el('newAssistantName').value.trim() || 'Assistant',
          llm_backend: el('newAssistantBackend').value.trim() || 'mock',
          llm_model: el('newAssistantModel').value.trim() || 'gpt-4o-mini',
          personality: {},
          llm_overrides: {},
        }),
      });
      await loadAssistants();
      await loadUsers();
    }

    async function saveAssistantLlm(assistantId, idx) {
      let overrides = {};
      try { overrides = JSON.parse(el('ao_' + idx).value || '{}'); } catch (_) { alert('Invalid overrides JSON'); return; }
      await api('/admin/assistants/' + assistantId + '/llm', {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({
          llm_backend: el('ab_' + idx).value.trim(),
          llm_model: el('am_' + idx).value.trim(),
          llm_overrides: overrides,
        }),
      });
      await loadAssistants();
    }

    async function saveAssistantPersonality(assistantId, idx) {
      let personality = {};
      try { personality = JSON.parse(el('ap_' + idx).value || '{}'); } catch (_) { alert('Invalid personality JSON'); return; }
      await api('/admin/assistants/' + assistantId + '/personality', {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({ personality }),
      });
      await loadAssistants();
    }

    async function loadDevices() {
      state.devices = await api('/admin/devices' + userQuery(), { headers: authHeaders(false) });
      renderDevicesTable();
      renderDeviceCreate();
      await syncTestDevices();
    }

    function renderDeviceCreate() {
      const box = el('deviceCreate');
      if (!state.globalAdmin) {
        box.innerHTML = '';
        return;
      }
      const selected = state.selectedUserId || '';
      box.innerHTML = `
        <div class="row">
          <div class="span-4"><input id="newDeviceName" placeholder="Device name" /></div>
          <div class="span-4"><button class="menu_button" onclick="createDeviceForUser()">Create Device For Selected User</button></div>
          <div class="span-4 muted">Selected user id: ${selected || 'none (pick in user filters)'}</div>
        </div>
      `;
    }

    async function createDeviceForUser() {
      if (!state.globalAdmin || !state.selectedUserId) {
        alert('Select a user in scope first.');
        return;
      }
      await api('/admin/users/' + state.selectedUserId + '/devices', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ name: el('newDeviceName').value.trim() || 'Device' }),
      });
      await loadDevices();
      await loadUsers();
    }

    function assistantsByUser(userId) {
      return state.assistants.filter((a) => a.user_id === userId);
    }

    function renderDevicesTable() {
      const rows = state.devices.map((d, i) => {
        const options = assistantsByUser(d.user_id)
          .map((a) => `<option value="${a.id}" ${a.id === d.assistant_id ? 'selected' : ''}>${esc(a.name)} (${a.id.slice(0,8)})</option>`)
          .join('');
        return `
          <tr>
            <td>${esc(d.name)}<div class="muted">${d.id}<br>${d.user_id}</div></td>
            <td>${d.platform || '-'}</td>
            <td>${d.client_version || '-'}</td>
            <td>${d.last_seen || '-'}</td>
            <td><select id="da_${i}">${options}</select></td>
            <td><button class="menu_button" onclick="bindDevice('${d.id}', ${i})">Bind</button></td>
          </tr>
        `;
      }).join('');

      el('devicesTable').innerHTML = rows
        ? `<table><thead><tr><th>Device</th><th>Platform</th><th>Version</th><th>Last Seen</th><th>Assistant</th><th></th></tr></thead><tbody>${rows}</tbody></table>`
        : '<div class="muted">No devices</div>';
    }

    async function bindDevice(deviceId, idx) {
      const assistantId = el('da_' + idx).value;
      if (!assistantId) {
        alert('Select an assistant first.');
        return;
      }
      await api('/admin/devices/' + deviceId + '/assistant', {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({ assistant_id: assistantId }),
      });
      await loadDevices();
    }

    async function syncTestDevices() {
      const select = el('testDevice');
      const options = state.devices.map((d) => `<option value="${d.id}">${esc(d.name)} (${d.id.slice(0,8)})</option>`);
      select.innerHTML = options.join('');
    }

    async function loadSession() {
      const id = el('testDevice').value;
      if (!id) return;
      const data = await api('/admin/devices/' + id + '/session', { headers: authHeaders(false) });
      el('sessionResult').textContent = JSON.stringify(data, null, 2);
    }

    async function runProbe() {
      const payload = {
        backend: el('probeBackend').value.trim() || 'mock',
        model: el('probeModel').value.trim() || 'gpt-4o-mini',
        prompt: el('probePrompt').value.trim() || 'Hello',
        llm_overrides: {},
      };
      const data = await api('/admin/providers/probe', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(payload),
      });
      el('probeResult').textContent = JSON.stringify(data, null, 2);
    }

    async function sendTestChat() {
      const id = el('testDevice').value;
      const text = el('testMessage').value.trim();
      if (!id || !text) return;
      const data = await api('/admin/test-chat/' + id, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ text }),
      });
      el('testChatResult').textContent = JSON.stringify(data, null, 2);
      await loadChatTurns();
    }

    async function loadChatTurns() {
      const params = new URLSearchParams();
      params.set('limit', String(Math.max(1, Math.min(500, Number(el('logLimit').value) || 30))));
      const statusFilter = el('logStatus').value;
      if (statusFilter) params.set('status', statusFilter);
      const scopedUser = selectedScopedUserId();
      if (scopedUser) params.set('user_id', scopedUser);

      const data = await api('/admin/chat-turns?' + params.toString(), { headers: authHeaders(false) });
      const rows = data.map((t) => `
        <tr>
          <td>${t.created_at}</td>
          <td class="${t.status === 'ok' ? 'ok' : 'err'}">${esc(t.status)}</td>
          <td>${esc(t.user_id)}</td>
          <td>${esc(t.provider)}<div class="muted">${esc(t.model)}</div></td>
          <td>${t.latency_ms || '-'}</td>
          <td>${esc((t.request_text || '').slice(0, 260))}</td>
          <td>${t.status === 'ok' ? esc((t.response_text || '').slice(0, 260)) : esc(t.error || '')}</td>
        </tr>
      `).join('');

      el('turnsTable').innerHTML = rows
        ? `<table><thead><tr><th>Time</th><th>Status</th><th>User</th><th>Provider/Model</th><th>Latency</th><th>Input</th><th>Output/Error</th></tr></thead><tbody>${rows}</tbody></table>`
        : '<div class="muted">No chat turns</div>';
    }

    bindTabs();

    if (state.token) {
      refreshAll().catch((e) => setStatus('Auth invalid: ' + e.message, false));
    }
  </script>
</body>
</html>
"""


@router.get("/admin", response_class=HTMLResponse)
async def admin_page() -> HTMLResponse:
    return HTMLResponse(content=ADMIN_HTML)
