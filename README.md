# FantasyArena

A full-stack fantasy sports platform demonstrating system design and implementation concepts.

---

## Prerequisites

| Tool | Version | Required For |
|------|---------|-------------|
| Python | 3.11+ | Backend |
| pip | latest | Backend deps |
| Node.js | 18+ | Graph Service |
| npm | latest | Graph Service deps |
| Neo4j | 5.x (optional) | Graph features |

Neo4j is **optional** — the backend and frontend run fully without it. Graph features degrade gracefully.

---

## Installation

### 1. Clone / extract the project

```
fantasyarena/
├── backend/
├── frontend/
└── graph-service/
```

### 2. Backend

```bash
cd fantasyarena/backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

`requirements.txt` includes:
```
fastapi==0.115.5
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-multipart==0.0.12
pydantic[email]==2.10.3
httpx==0.27.2
aiofiles==24.1.0
```

### 3. Graph Service (optional)

```bash
cd fantasyarena/graph-service
npm install
```

### 4. Neo4j (optional)

Download Neo4j Desktop from https://neo4j.com/download or run via Docker:

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5
```

---

## Running the Application

### Terminal 1 — Backend (required)

```bash
cd fantasyarena/backend
source venv/bin/activate

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will:
- Create `fantasyarena.db` (SQLite) automatically
- Seed 22 cricket players on first boot
- Register all event bus handlers

### Terminal 2 — Graph Service (optional)

```bash
cd fantasyarena/graph-service

# Default (connects to bolt://localhost:7687)
npm start

# Custom Neo4j connection
NEO4J_URI=bolt://localhost:7687 \
NEO4J_USER=neo4j \
NEO4J_PASSWORD=password \
npm start
```

### Terminal 3 — Frontend

Serve the frontend folder with any static file server:

```bash
# Option A: Python (simplest)
cd fantasyarena/frontend
python -m http.server 3000

# Option B: Node
npx serve fantasyarena/frontend -p 3000
```

Then open: **http://localhost:3000**

The backend also serves the frontend at: **http://localhost:8000/app**

---

## First-Time Setup (100% UI — no terminal commands)

1. Open **http://localhost:3000** (or `http://localhost:8000/app`)
2. You'll be redirected to the **First Time Setup** page automatically (no admin exists yet)
3. Fill in the form to create your **admin account** — this is the only admin creation step, and it's done entirely in the browser
4. You're auto-logged in and redirected to the **Admin Panel**

From here, everything is point-and-click:

- **Admin Panel → Contests tab** — create contests with a form (name, entry fee, prize pool, max teams, start time)
- **Admin Panel → Matches tab** — create matches, link them to contests, start/complete them, and trigger live scoring events (wicket, six, four, etc.) with dropdowns
- **Admin Panel → Users tab** — view all users and promote any user to admin with one click
- **Admin Panel → Metrics / Logs tabs** — live system monitoring

To create additional player accounts, just open an incognito window (or have a friend) and click **Create account** on the login page — each new account gets **₹1000** wallet balance automatically.

---

## Quick Walkthrough (UI-based)

1. **Setup** → create admin account on first visit (one-time)
2. **Admin Panel → Contests** → create a contest via the form
3. **Register** (as a player, separate browser/incognito) → auto-credited ₹1000
4. **Contests page** → click **Build Team & Join** → guided 3-step wizard:
   - Step 1: pick 11 players, assign captain (C) and vice-captain (VC)
   - Step 2: review squad, credits, role breakdown
   - Step 3: confirm entry fee deduction and join
5. **My Teams** → view full squads, delete unlocked teams
6. **Admin Panel → Matches** → create a match linked to the contest, click **Start**
7. **Live Match Center** (player view) → auto-detects the live match for joined contests, shows live event feed + live leaderboard via WebSocket
8. **Admin Panel → Matches** → trigger events (wicket/six/four/catch/etc.) via dropdown — scores update live for all connected players
9. **Admin Panel → Matches** → click **Complete** → prizes auto-distributed to wallets
10. **Dashboard / Profile** → see updated wallet balance, total winnings, contests joined

---

## API Reference

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /admin/setup/status | — | Check if any admin exists |
| POST | /admin/setup/first-admin | — | Create the first admin (one-time, UI-driven) |
| POST | /auth/register | — | Register user |
| POST | /auth/login | — | Login, get JWT |
| GET | /users/me | JWT | Get profile |
| PATCH | /users/me | JWT | Update profile (name, email) |
| GET | /users/me/summary | JWT | Dashboard stats (contests joined, winnings, teams) |
| GET | /wallet/balance | JWT | Get balance |
| POST | /wallet/deposit | JWT | Add funds |
| POST | /wallet/withdraw | JWT | Withdraw funds |
| GET | /wallet/transactions | JWT | Transaction history |
| GET | /contests | JWT | List contests |
| POST | /admin/contests | Admin | Create contest (admin panel form) |
| GET | /contests/{id} | JWT | Get contest detail |
| POST | /contests/{id}/join | JWT | Join with team |
| GET | /teams/players/all | JWT | Player pool |
| POST | /teams | JWT | Create team |
| GET | /teams | JWT | My teams (with full roster) |
| GET | /teams/{id} | JWT | Get team detail |
| DELETE | /teams/{id} | JWT | Delete unlocked team |
| POST | /admin/matches | Admin | Create match (admin panel form) |
| POST | /admin/matches/{id}/start | Admin | Start match |
| POST | /admin/matches/{id}/complete | Admin | End match + distribute prizes |
| GET | /scoring/matches | JWT | List matches |
| POST | /scoring/event | Admin | Trigger match event |
| GET | /leaderboard/{contest_id} | JWT | Get leaderboard |
| GET | /notifications | JWT | Get notifications |
| GET | /notifications/unread-count | JWT | Unread count (nav badge) |
| PATCH | /notifications/{id}/read | JWT | Mark one as read |
| PATCH | /notifications/read-all | JWT | Mark all as read |
| WS | /ws/match/{match_id} | — | Live match feed |
| WS | /ws/leaderboard/{contest_id} | — | Live leaderboard |
| GET | /admin/users | Admin | View all users + balances |
| POST | /admin/promote/{username} | Admin | Promote user to admin |
| GET | /admin/teams | Admin | View all teams |
| GET | /admin/transactions | Admin | View all transactions |
| GET | /admin/metrics | Admin | System metrics |
| GET | /admin/logs | Admin | System logs |

Graph Service (port 4000):

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /graph/relationships | Write relationship |
| GET | /graph/relationships/contest/{id}/participants | Contest participants |
| GET | /graph/relationships/player/{id}/teams | Teams with player |
| GET | /graph/recommendations/{user_id} | Contest recommendations |
| GET | /graph/recommendations/{user_id}/players | Player recommendations |

---

## Environment Variables

### Backend (optional overrides)

```bash
JWT_SECRET=your-secret-key-here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
GRAPH_SERVICE_URL=http://localhost:4000
DEBUG=true
```

### Graph Service

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
PORT=4000
```

---

## Architecture

```
Browser
  │
  ├── HTTP/REST ──► FastAPI (port 8000)   ← API Gateway (Facade Pattern)
  │                    │
  │                    ├── /auth          ← Auth Service    (JWT Proxy Pattern)
  │                    ├── /wallet        ← Payment Service
  │                    ├── /contests      ← Contest Service (Factory Pattern)
  │                    ├── /teams         ← Team Service
  │                    ├── /scoring       ← Scoring Service (Strategy Pattern)
  │                    ├── /leaderboard   ← Leaderboard Service
  │                    ├── /notifications ← Notification Service
  │                    └── /admin         ← Admin Service
  │                    │
  │                    ├── SQLite DB (via SQLAlchemy)
  │                    └── In-process Event Bus (Observer Pattern)
  │                              │
  │                              └── match.event
  │                                    → leaderboard.updated
  │                                    → notification.send
  │
  ├── WebSocket ──► FastAPI /ws/*         ← Real-time push
  │
  └── HTTP ──────► Express (port 4000)   ← Graph Service
                       └── Neo4j (bolt://localhost:7687)
```

---

## Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| Facade | `main.py` | API Gateway — single entry to all services |
| Proxy | `middleware/auth_middleware.py` | JWT auth on every protected route |
| Observer | `event_bus.py` + `event_handlers.py` | match event → score → leaderboard → notify |
| Factory | `services/contest_service.py` `ContestFactory` | Contest creation with validation |
| Strategy | `services/scoring_service.py` `ScoringStrategy` | Sport-specific scoring rules |
| Adapter | `ScoringStrategyFactory` | Maps raw events to scoring strategies |

---

## System Design Concepts

| Concept | Implementation |
|---------|---------------|
| CAP Theorem | SQLite = CP. Notes in `main.py` on Cassandra (AP) for scale |
| Event-Driven | In-process EventBus; production → Kafka |
| Pub/Sub | `bus.subscribe / bus.publish` in `event_bus.py` |
| WebSockets | `routers/websocket.py` — ConnectionManager per room |
| Horizontal Scale | WS manager note: Redis Pub/Sub for multi-instance |
| Caching | Leaderboard in-memory sort; production → Redis sorted set |
| Sharding | Noted in `main.py`; user_id % N for users table |
| Replication | SQLite WAL mode; production → PostgreSQL primary + replicas |
| JWT Auth | `services/auth_service.py` + `middleware/auth_middleware.py` |
| Password Hashing | bcrypt via passlib |
| Structured Logging | `logger.py` JSONFormatter |
| Metrics | `logger.py` MetricsStore → `/metrics` endpoint |
| Request Tracing | `RequestLoggingMiddleware` adds X-Request-ID header |
| Microservices | Logically separated routers/services, co-deployed |
| Service Discovery | Config-driven (`config.py` GRAPH_SERVICE_URL) |
| Fault Tolerance | Payment rollback in `payment_service.deduct_entry_fee` |

---

## Project Structure

```
fantasyarena/
├── backend/
│   ├── main.py                  # FastAPI app + API Gateway
│   ├── config.py                # Settings
│   ├── database.py              # SQLAlchemy engine + session
│   ├── event_bus.py             # Pub/Sub event bus (Observer)
│   ├── event_handlers.py        # match → leaderboard → notification pipeline
│   ├── logger.py                # Structured JSON logging + metrics
│   ├── seed.py                  # Player pool seed data
│   ├── requirements.txt
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── routers/                 # HTTP route handlers
│   ├── services/                # Business logic
│   ├── middleware/              # JWT auth proxy
│   └── admin/                   # Admin panel backend
├── graph-service/
│   ├── index.js                 # Express app entry
│   ├── neo4j.js                 # Neo4j driver
│   ├── package.json
│   └── routes/
│       ├── relationships.js     # Write + query graph relationships
│       └── recommendations.js  # Cypher collaborative filtering
└── frontend/
    ├── index.html               # Login (auto-detects first-run)
    ├── setup.html               # First-time admin setup (UI-based, one-time)
    ├── register.html            # Player registration
    ├── dashboard.html           # Stats, live ticker, my teams, notifications
    ├── contests.html            # Browse contests + 3-step join wizard
    ├── myteams.html             # Manage all teams (view roster, delete unlocked)
    ├── live-match.html          # WebSocket live feed for joined contests
    ├── leaderboard.html         # WebSocket real-time ranks
    ├── wallet.html               # Deposit/withdraw/transaction history
    ├── notifications.html       # All notifications, mark as read
    ├── profile.html             # Edit profile, account stats
    ├── admin.html               # Admin panel (contests, matches, users, metrics, logs)
    ├── css/styles.css
    └── js/
        ├── api.js               # Fetch wrapper + JWT
        ├── nav.js               # Shared navbar (with notification badge, avatar)
        └── toast.js             # Toast notifications
```
