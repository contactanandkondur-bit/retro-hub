-- Scrum Master Table
CREATE TABLE IF NOT EXISTS scrum_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Retro Sessions Table
CREATE TABLE IF NOT EXISTS retro_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sprint_name TEXT NOT NULL,
    sprint_goal TEXT,
    team_size INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    passcode TEXT NOT NULL,
    status TEXT DEFAULT 'active',  -- active | closed | approved
    summary_token TEXT UNIQUE,     -- for public shareable link
    email_recipients TEXT,         -- comma separated emails
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Submissions Table
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    went_well TEXT,
    improve TEXT,
    recognition TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES retro_sessions(id)
);

-- AI Summaries Table
CREATE TABLE IF NOT EXISTS ai_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER UNIQUE NOT NULL,
    went_well_summary TEXT,
    improve_summary TEXT,
    recognition_summary TEXT,
    action_items_summary TEXT,
    is_edited INTEGER DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES retro_sessions(id)
);

-- Action Items Table
CREATE TABLE IF NOT EXISTS action_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    sprint_name TEXT NOT NULL,
    item_text TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES retro_sessions(id)
);