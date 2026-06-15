# DRINKOO Frontend

React 18 + Vite + Tailwind CSS frontend for the DRINKOO RAG chatbot application.

## Pages

- **Home** (`/`) — Landing page with feature overview and suggested chat questions
- **Login** (`/login`) — Login form with JWT authentication
- **Signup** (`/signup`) — Account creation form with validation
- **Chat** (`/chat`) — Protected RAG chatbot UI with grounded answers and context inspector
- **Upload** (`/upload`) — Protected image upload with drag-and-drop, type and size validation
- **Status** (`/status`) — System health page showing API, database, and RAG readiness

## Tech Stack

- React 18
- React Router v6 (client-side routing)
- Vite 5 (dev server + build tool)
- Tailwind CSS v3 (utility-first styling)
- Axios (HTTP client with JWT interceptors)

## Setup

```bash
npm install
npm run dev       # Development server on http://localhost:5173
npm run build     # Production build → dist/
npm run preview   # Preview production build
```

During development, Vite proxies `/api/*` requests to the FastAPI backend on port 8000.

## Auth flow

- JWT access token stored in `localStorage` under key `drinkoo_token`.
- Axios interceptor attaches token to every request header.
- On 401 response, token is cleared and user is redirected to `/login`.
- `ProtectedRoute` component wraps `/chat` and `/upload` — unauthenticated users are redirected to login.

## Building for production

```bash
npm run build
```

FastAPI serves the resulting `dist/` folder as static files. The catch-all route returns `index.html`
for all non-API paths so React Router handles navigation correctly.
