# Multi-Stream Operations

A Python-based desktop application for multi-streaming to Kick, Twitch, and YouTube using OBS Studio.

## Features

- Simultaneous streaming to multiple platforms
- Modular architecture for extensibility
- Tracking of viewers, followers, subscribers, and donations
- Multi-platform chat integration
- Backend API for metrics and chat storage

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python src/main.py`

## Backend Deployment

The backend is deployed on Render with Neon PostgreSQL database.

### Environment Variables

Set the following environment variables in your Render service:

- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `PORT`: Port for the server (default: 10000)

### Deploying to Render

1. Push the backend code to GitHub (already done)
2. Connect your GitHub repo to Render
3. Create a new Web Service
4. Set the build command: `npm install`
5. Set the start command: `node server.js`
6. Add environment variables
7. Deploy

### Updating Backend URL

After deployment, update the `BACKEND_URL` in `src/config.py` with your Render app URL.

## Usage

1. Start OBS Studio with WebSocket enabled
2. Run the application
3. Configure your platform API keys via environment variables
4. Start streaming and monitor metrics

## Contributing

[Add contributing guidelines here]

## License

[Add license here]