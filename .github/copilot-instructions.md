# Multi-Stream Operations - Development Guidelines

## Project Overview
Python desktop application for multi-streaming to Kick, Twitch, and YouTube using OBS Studio.

## Architecture
- **Frontend**: Tkinter GUI (`src/gui.py`)
- **Backend**: Node.js/Express API on Render (`backend/`)
- **Database**: Neon PostgreSQL

## Code Standards
- Use type hints for function parameters and returns
- Include docstrings for all classes and public methods
- Follow PEP 8 style guidelines
- Keep functions focused and under 50 lines

## Key Components
- `config.py` - Environment configuration
- `gui.py` - Main application interface
- `obs_integration.py` - OBS WebSocket control
- `platform_apis.py` - Twitch/YouTube/Kick integrations
- `metrics_aggregator.py` - Unified metrics collection
- `chat_manager.py` - Multi-platform chat handling

## Testing
- Run tests with `pytest tests/`
- Add tests for new features in `tests/` directory

## Deployment
- Backend: https://multi-stream-backend.onrender.com
- Database: Neon PostgreSQL (connection in Render env vars)