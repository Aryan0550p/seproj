# YUMSIE Wholesale Distribution System

YUMSIE is a Vue 3 wholesale distribution workspace with role-based dashboards, local persistence, and an admin-focused operations layer. The current build includes live metrics, AI-style chat assistance, and user administration features for the built-in admin account.

## What It Does

- Admin dashboard with live operational metrics and a user-management modal
- Registered user listing with delete support for non-protected accounts
- Salesman and retailer role dashboards
- Inventory, orders, payments, delivery, reports, customer, and performance pages
- Floating AI assistant that returns live figures from the current store state
- Theme switching with dark/light support

## Current Feature Set

### Admin

- View all registered users
- Create new salesman and retailer users
- Delete non-protected users
- See live counts for orders, revenue, users, and pending deliveries
- Use the assistant to query exact figures for pending orders, payments, stock, and revenue

### Salesman

- View sales dashboard and performance pages
- Track customers and sales orders
- Ask the assistant for live order and payment totals

### Retailer

- View a dedicated retailer dashboard
- Access role-limited navigation only
- Ask the assistant for live order status and account-related figures

## Data Model

- Auth users are stored in `localStorage` under `yumsie_auth_user` and `yumsie_db_users`
- Products, orders, alerts, logs, notifications, and stock records are stored in `localStorage` through the shared store
- The backend Flask service persists its own state in SQLite at `backend/yumsie.db`
- Seed data is restored automatically when the app initializes for the first time

## Tech Stack

- Frontend: Vue 3, Vue Router, Vite
- Backend: Flask, Flask-CORS, SQLite
- State: Local-storage-backed store and auth helpers
- Styling: Vanilla CSS with a shared theme system

## Repository Layout

```
backend/
├── app.py                 # Flask API for health and core data routes
├── services/
│   └── store_service.py   # SQLite-backed business data service
└── README.md              # Backend snapshot

frontend/
├── src/
│   ├── App.vue            # App shell with global AI assistant
│   ├── auth.js            # Role/auth helpers and user management
│   ├── store.js           # Shared local data store
│   ├── components/
│   │   ├── Navbar.vue
│   │   ├── Footer.vue
│   │   └── AiChatWidget.vue
│   ├── pages/             # Role-based dashboards and operational pages
│   └── router/
│       └── index.js

src/
├── App.vue                # Root copy of the frontend app shell
├── auth.js
├── store.js
├── components/
│   └── AiChatWidget.vue
└── pages/
```

## AI Assistant

The assistant is intentionally data-driven. It reads the live store and answers with exact values such as:

- total orders
- pending orders
- shipped, delivered, and cancelled orders
- unpaid orders and pending payment amount
- total and paid revenue
- registered user count
- low-stock and out-of-stock products

Example prompts:

- Live KPI snapshot
- Pending orders
- Pending payments
- Revenue summary
- Low stock products
- Out of stock products
- Users count

## Running Locally

### Prerequisites

- Node.js 18+ 
- npm
- Python 3.10+ for the backend

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
python backend/app.py
```

The backend listens on port `5000` and the frontend runs on port `3000` in this workspace.

## Validation

- Frontend production build succeeds with `vite build`
- Backend health check returns `{"status":"ok"}` at `/api/health`

## Notes

- The workspace contains mirrored frontend source trees at `src/` and `frontend/src/`; both are kept in sync.
- The assistant is frontend-only and reads live application data from the store, so it does not require an external AI service.

## License

© 2026 YUMSIE Wholesale Distribution System. All rights reserved.
