function buildNav(activePage) {
  const user = api.getUser();
  if (!user) { window.location.href = "index.html"; return; }

  const links = [
    { href: "dashboard.html",    label: "Dashboard",   key: "dashboard" },
    { href: "contests.html",     label: "Contests",    key: "contests" },
    { href: "myteams.html",      label: "My Teams",    key: "myteams" },
    { href: "live-match.html",   label: "Live",        key: "live" },
    { href: "leaderboard.html",  label: "Leaderboard", key: "leaderboard" },
    { href: "wallet.html",       label: "Wallet",      key: "wallet" },
    { href: "notifications.html",label: "Alerts",      key: "notifications" },
  ];
  if (user.is_admin) links.push({ href: "admin.html", label: "Admin", key: "admin" });

  const navLinks = links.map(l => {
    const badge = l.key === "notifications" ? '<span id="notif-badge" class="notif-dot" style="display:none"></span>' : "";
    return `<a href="${l.href}" class="${l.key === activePage ? 'active' : ''}">${l.label}${badge}</a>`;
  }).join("");

  const nav = document.createElement("nav");
  nav.className = "navbar";
  nav.innerHTML = `
    <div class="container">
      <a href="dashboard.html" class="nav-logo">Fantasy<span>Arena</span></a>
      <div class="nav-links">
        ${navLinks}
        <span class="nav-wallet" id="nav-wallet">₹ —</span>
        <a href="profile.html" class="${activePage === 'profile' ? 'active' : ''}" title="Profile" style="padding:0.4rem 0.6rem">
          <span id="nav-avatar" style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:var(--accent-gold);color:#0B1120;font-family:'Rajdhani',sans-serif;font-weight:700;font-size:0.75rem">${user.username.charAt(0).toUpperCase()}</span>
        </a>
        <button onclick="doLogout()" class="btn btn-secondary btn-sm">Sign Out</button>
      </div>
    </div>`;
  document.body.prepend(nav);

  // Load wallet balance into nav
  api.get("/wallet/balance").then(d => {
    const el = document.getElementById("nav-wallet");
    if (el && d) el.textContent = `₹ ${d.balance.toFixed(2)}`;
  }).catch(() => {});

  // Load unread notification count
  api.get("/notifications/unread-count").then(d => {
    const badge = document.getElementById("notif-badge");
    if (badge && d && d.unread_count > 0) badge.style.display = "inline-block";
  }).catch(() => {});
}

function doLogout() {
  api.clearAuth();
  window.location.href = "index.html";
}

window.buildNav = buildNav;
window.doLogout = doLogout;
