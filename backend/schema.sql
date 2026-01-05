-- Create metrics table
CREATE TABLE metrics (
  id SERIAL PRIMARY KEY,
  viewers INTEGER DEFAULT 0,
  followers INTEGER DEFAULT 0,
  subscribers INTEGER DEFAULT 0,
  donations DECIMAL(10,2) DEFAULT 0.0,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Create chat_logs table
CREATE TABLE chat_logs (
  id SERIAL PRIMARY KEY,
  message TEXT,
  platform VARCHAR(50),
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Insert sample data
INSERT INTO metrics (viewers, followers, subscribers, donations) VALUES (100, 500, 50, 25.50);