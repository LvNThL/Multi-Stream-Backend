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
let pool;
if (process.env.DATABASE_URL) {
  pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
  });

  // Test DB connection
  pool.connect((err) => {
    if (err) {
      console.error('Database connection error:', err.message);
      console.log('Continuing without database connection...');
    } else {
      console.log('Connected to Neon PostgreSQL');
    }
  });
} else {
  console.log('No DATABASE_URL provided, running without database');
}

// Routes
app.get('/metrics', async (req, res) => {
  if (!pool) {
    return res.json({ viewers: 0, followers: 0, subscribers: 0, donations: 0.0 });
  }
  try {
    // Placeholder: Fetch aggregated metrics from DB or APIs
    const result = await pool.query('SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 1');
    res.json(result.rows[0] || { viewers: 0, followers: 0, subscribers: 0, donations: 0.0 });
  } catch (err) {
    console.error('Database query error:', err.message);
    res.status(500).json({ error: 'Database error', details: err.message });
  }
});

app.post('/chat/send', async (req, res) => {
  const { message, platform } = req.body;
  if (!pool) {
    return res.json({ success: true, note: 'No database connection - message not stored' });
  }
  try {
    // Placeholder: Send message to platforms and log to DB
    await pool.query('INSERT INTO chat_logs (message, platform, timestamp) VALUES ($1, $2, NOW())', [message, platform]);
    res.json({ success: true });
  } catch (err) {
    console.error('Database insert error:', err.message);
    res.status(500).json({ error: 'Database error', details: err.message });
  }
});

app.get('/chat/messages', async (req, res) => {
  if (!pool) {
    return res.json([]);
  }
  try {
    const result = await pool.query('SELECT * FROM chat_logs ORDER BY timestamp DESC LIMIT 50');
    res.json(result.rows);
  } catch (err) {
    console.error('Database query error:', err.message);
    res.status(500).json({ error: 'Database error', details: err.message });
  }
});

// Start server
app.listen(port, '0.0.0.0', () => {
  console.log(`Backend server running on port ${port}`);
});