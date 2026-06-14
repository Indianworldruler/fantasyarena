const BASE_URL = "https://fantasyarena-euzq.onrender.com";

function getToken() {
  return localStorage.getItem("fa_token");
}

function setAuth(token, user) {
  localStorage.setItem("fa_token", token);
  localStorage.setItem("fa_user", JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem("fa_token");
  localStorage.removeItem("fa_user");
}

function getUser() {
  const u = localStorage.getItem("fa_user");
  return u ? JSON.parse(u) : null;
}

function isLoggedIn() {
  return !!getToken();
}

async function request(method, path, body = null, auth = true) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (!token) {
      window.location.href = "/index.html";
      return;
    }
    headers["Authorization"] = `Bearer ${token}`;
  }

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE_URL}${path}`, opts);

  if (res.status === 401) {
    clearAuth();
    window.location.href = "/index.html";
    return;
  }

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || JSON.stringify(data) || "Request failed");
  }
  return data;
}

const api = {
  get:    (path, auth = true)        => request("GET",    path, null, auth),
  post:   (path, body, auth = true)  => request("POST",   path, body, auth),
  patch:  (path, body, auth = true)  => request("PATCH",  path, body, auth),
  delete: (path, auth = true)        => request("DELETE", path, null, auth),
  setAuth, clearAuth, getUser, isLoggedIn, getToken,
};

window.api = api;
