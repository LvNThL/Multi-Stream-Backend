require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Neon PostgreSQL connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

// Test DB connection
pool.connect((err) => {
  if (err) {
    console.error('Database connection error:', err);
  } else {
    console.log('Connected to Neon PostgreSQL');
  }
});

// Routes
app.get('/metrics', async (req, res) => {
  try {
    // Placeholder: Fetch aggregated metrics from DB or APIs
    const result = await pool.query('SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 1');
    res.json(result.rows[0] || { viewers: 0, followers: 0, subscribers: 0, donations: 0.0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/chat/send', async (req, res) => {
  const { message, platform } = req.body;
  try {
    // Placeholder: Send message to platforms and log to DB
    await pool.query('INSERT INTO chat_logs (message, platform, timestamp) VALUES ($1, $2, NOW())', [message, platform]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/chat/messages', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM chat_logs ORDER BY timestamp DESC LIMIT 50');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Start server
app.listen(port, () => {
  console.log(`Backend server running on port ${port}`);
});