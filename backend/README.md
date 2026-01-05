# Multi-Stream Backend

Node.js backend for the Multi-Stream Operations app.

## Setup

1. Install dependencies: `npm install`
2. Set up Neon PostgreSQL database and update `.env` with your connection string.
3. Run the schema: Use Neon's SQL editor or psql to execute `schema.sql`.
4. Start the server: `npm run dev` (for development) or `npm start` (for production).

## Endpoints

- `GET /metrics`: Fetch current aggregated metrics.
- `POST /chat/send`: Send a chat message (body: { message, platform }).
- `GET /chat/messages`: Fetch recent chat messages.

## Deployment

Deploy to Render: Connect your GitHub repo, set environment variables (DATABASE_URL), and deploy.