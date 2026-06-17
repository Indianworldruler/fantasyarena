# FantasyArena

## Project Overview

FantasyArena is an online fantasy sports platform inspired by Dream11. The application allows users to create fantasy teams, join contests, participate in simulated live matches, earn fantasy points based on player performance, track leaderboard rankings, receive notifications, and manage wallet rewards.

The project is built as a System Design and Implementation application. It demonstrates a fantasy sports architecture using a Python FastAPI backend, SQLAlchemy-based local database storage, JWT authentication, frontend pages built with HTML, CSS, and JavaScript, simulated live match events, scoring logic, leaderboard updates, wallet transactions, notifications, and an admin panel.

The system follows a microservice-style modular structure where separate backend routers and services handle authentication, contests, teams, scoring, leaderboards, payments, notifications, admin operations, and WebSocket/live update functionality. It also demonstrates important system design concepts such as real-time event processing, low-latency leaderboard updates, fault tolerance, secure transaction handling, scalability, and fairness in scoring.

---

## Live Application Links

### NOTE: If you want to run using the live hosted link, Firstly open the backend link, Wait for a minute then open the frontend link. Rest all the instructions given in the README.md file for the offline run of  the app. Steps to use the app are in the documentation Phase 1. 


The application can also be accessed online using the deployed Render links below.

Frontend:

```text
https://fantasyarena-frontend.onrender.com
```

Backend API:

```text
https://fantasyarena-euzq.onrender.com
```

Documentation:

```text
https://docs.google.com/document/d/1jg2-l1Yr9yDWzrhStNamG4C0sZuTrI8JeOHDPQkpPsw/edit?tab=t.0
```

---

## Setup Instructions

### 1. Open Terminal

Open the terminal and go to the project folder.

```bash
cd fantasyarena
```

---

### 2. Backend Setup

Go to the backend folder.

```bash
cd backend
```

Create a Python virtual environment.

```bash
python3 -m venv venv
```

Activate the virtual environment.

```bash
source venv/bin/activate
```

Install backend dependencies from `requirements.txt`.

```bash
pip install -r requirements.txt
```

---

### 3. VS Code Interpreter Fix

If VS Code shows errors such as `fastapi could not be resolved`, create a `.vscode/settings.json` file in the main project folder.

From the project root:

```bash
mkdir -p .vscode
nano .vscode/settings.json
```

Paste this:

```json
{
  "python.defaultInterpreterPath": "/Users/parthsahani/Desktop/fantasyarena/backend/venv/bin/python",
  "python.analysis.extraPaths": [
    "/Users/parthsahani/Desktop/fantasyarena/backend"
  ]
}
```

Save the file, then reload VS Code.

```text
Cmd + Shift + P
Developer: Reload Window
```

This helps VS Code use the correct backend virtual environment.

---

### 4. Frontend Setup

Open another terminal and go to the frontend folder.

```bash
cd fantasyarena/frontend
```

Install frontend dependencies if required.

```bash
npm install
```

The frontend mainly uses HTML, CSS, and JavaScript.

---

## Dependencies

### Backend Dependencies

The backend dependencies are stored in:

```text
backend/requirements.txt
```

Install them using:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

Main backend technologies used:

```text
FastAPI
Uvicorn
SQLAlchemy
Python-Jose
Passlib
Bcrypt
Pydantic
Python-Multipart
HTTPX
Aiofiles
```

### Frontend Dependencies

The frontend is built using:

```text
HTML
CSS
JavaScript
```

If the project includes frontend package dependencies, install them using:

```bash
cd frontend
npm install
```

---

## Running the Application Locally

### 1. Run Backend

Open terminal and go to the backend folder.

```bash
cd fantasyarena/backend
```

Activate the virtual environment.

```bash
source venv/bin/activate
```

Run the FastAPI backend.

```bash
uvicorn main:app --port 8000 --reload
```

Backend will run at:

```text
http://localhost:8000
```

API documentation will be available at:

```text
http://localhost:8000/docs
```

---

### 2. Run Frontend

Open another terminal and go to the frontend folder.

```bash
cd fantasyarena/frontend
```

Run the frontend using Python HTTP server.

```bash
python -m http.server 3000
```

Open the application in browser:

```text
http://localhost:3000
```

---

## Execution Steps

### 1. Create Admin Account

Open the application and create a new admin account using the following details:

```text
Username: admin
Full Name: Site Admin
Email: admin@arena.com
Password: admin123
```

After registering, log in using the admin account.

---

### 2. Open Admin Panel

After logging in as admin, you will reach the admin dashboard. From the top navigation bar, click on the **Admin** tab on the right side.

The admin panel is used to manage contests, matches, users, teams, transactions, leaderboard data, and simulated live events.

---

### 3. Create a Contest

Inside the Admin section, open the **Contests** tab.

Create a new contest by entering the required contest details such as sport type, contest name, entry fee, prize pool, and participant limit.

This contest will later be visible to normal users.

---

### 4. Create a Normal User Account

Sign out from the admin account.

Create a new normal user account with any valid user details.

Then log in using the newly created user account.

---

### 5. Join a Contest

After logging in as a user, go to the **Contests** tab.

Select the contest created by the admin.

Click on **Build Team** or **Join**.

Select the players you want in your fantasy team. Review your selected team and confirm.

Once confirmed, the user successfully joins the contest.

For demo purposes, one user is enough. For a better experience, multiple users can be created and the same process can be repeated.

---

### 6. Create and Start a Match

Log out from the user account and log in again as admin.

Go to the **Admin** tab.

Open the **Matches** section.

Create a new match by entering the required match details.

After creating the match, scroll down and start or live the match.

This makes the match active for simulated events.

---

### 7. Trigger Live Match Events

Inside the Admin panel, trigger match events by selecting a player and choosing an event.

For example, trigger events such as runs, wickets, goals, assists, or other sport-specific actions.

To demonstrate scoring clearly, trigger events for the players selected by the user’s fantasy team. When those players perform well, the user earns fantasy points.

---

### 8. View Leaderboard and Notifications

Fantasy points are updated based on triggered player events.

The updated points can be viewed in the **Leaderboard** section.

The user can also log back into the user account to view:

```text
Live score updates
Leaderboard rank
Notifications
Wallet updates
Contest status
```

This shows the real-time fantasy sports experience where users gain points based on player performance.

---

### 9. Finish the Match

Log in again as admin.

Go to the **Admin** tab and scroll to the match controls.

End or finish the match.

After the match is completed, the top-ranked user receives the reward or prize amount in the wallet.

The user can log back in and check notifications and wallet balance to confirm the reward.

---

## Final Demo Flow

The complete application flow is:

```text
Admin creates contest
User creates fantasy team
User joins contest
Admin creates and starts match
Admin triggers player events
System calculates fantasy points
Leaderboard updates dynamically
User receives notifications
Admin finishes match
Top player receives reward
```

This demonstrates a Dream11-style fantasy sports application where the user builds a team, joins a contest, earns points based on player performance, and wins rewards based on leaderboard ranking.

Khelegi India, Jeetegi India.


