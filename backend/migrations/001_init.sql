-- Migration 001: initial schema for Top Scoot MVP
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Administrative users for the backend panel
CREATE TABLE IF NOT EXISTS users (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    role           TEXT NOT NULL CHECK (role IN ('admin', 'editor')),
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    last_login_at  TEXT
);

-- Audit log for tracking changes in the admin panel
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    entity      TEXT NOT NULL CHECK (entity IN ('rider', 'event', 'result', 'system')),
    entity_id   INTEGER,
    action      TEXT NOT NULL,
    payload_json TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Riders participating in events
CREATE TABLE IF NOT EXISTS riders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname    TEXT NOT NULL,
    fullname    TEXT,
    city        TEXT NOT NULL,
    birthdate   TEXT NOT NULL,
    style       TEXT NOT NULL CHECK (style IN ('street', 'park', 'universal')),
    level       TEXT NOT NULL CHECK (level IN ('novice', 'amateur', 'pro')),
    photo_url   TEXT,
    socials_json TEXT,
    email       TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (nickname COLLATE NOCASE)
);

-- Events (tournaments)
CREATE TABLE IF NOT EXISTS events (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    date_start          TEXT NOT NULL,
    date_end            TEXT,
    city                TEXT NOT NULL,
    level               TEXT NOT NULL CHECK (level IN ('local', 'regional', 'national', 'international')),
    participants_count  INTEGER,
    style               TEXT CHECK (style IN ('street', 'park', 'universal')),
    has_best_trick      INTEGER NOT NULL DEFAULT 0 CHECK (has_best_trick IN (0, 1)),
    source_url          TEXT,
    organizer_contact   TEXT,
    status              TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Results linking riders and events
CREATE TABLE IF NOT EXISTS results (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id       INTEGER NOT NULL,
    rider_id       INTEGER NOT NULL,
    place          INTEGER,
    is_finalist    INTEGER NOT NULL DEFAULT 0 CHECK (is_finalist IN (0, 1)),
    is_participant INTEGER NOT NULL DEFAULT 0 CHECK (is_participant IN (0, 1)),
    points         INTEGER NOT NULL,
    comment        TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (rider_id) REFERENCES riders(id) ON DELETE CASCADE,
    UNIQUE (event_id, rider_id)
);

-- Cached rolling season points per rider
CREATE TABLE IF NOT EXISTS season_points (
    rider_id           INTEGER PRIMARY KEY,
    season_points      INTEGER NOT NULL DEFAULT 0,
    season_updated_at  TEXT,
    FOREIGN KEY (rider_id) REFERENCES riders(id) ON DELETE CASCADE
);

-- Helpful indexes for common queries
CREATE INDEX IF NOT EXISTS idx_results_event_id ON results(event_id);
CREATE INDEX IF NOT EXISTS idx_results_rider_id ON results(rider_id);
CREATE INDEX IF NOT EXISTS idx_events_date_start ON events(date_start);
CREATE INDEX IF NOT EXISTS idx_riders_filters ON riders(city, level, style);

COMMIT;
