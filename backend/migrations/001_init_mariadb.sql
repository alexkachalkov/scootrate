-- Migration 001: initial schema for Top Scoot MVP (MariaDB version)

START TRANSACTION;

-- Administrative users for the backend panel
CREATE TABLE IF NOT EXISTS users (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    email          VARCHAR(255) NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    role           VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'editor')),
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at  TIMESTAMP NULL
);

-- Audit log for tracking changes in the admin panel
CREATE TABLE IF NOT EXISTS audit_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT,
    entity      VARCHAR(50) NOT NULL CHECK (entity IN ('rider', 'event', 'result', 'system')),
    entity_id   INT,
    action      VARCHAR(50) NOT NULL,
    payload_json TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Riders participating in events
CREATE TABLE IF NOT EXISTS riders (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nickname    VARCHAR(255) NOT NULL,
    fullname    VARCHAR(255),
    city        VARCHAR(255) NOT NULL,
    birthdate   DATE NOT NULL,
    style       VARCHAR(50) NOT NULL CHECK (style IN ('street', 'park', 'universal')),
    level       VARCHAR(50) NOT NULL CHECK (level IN ('novice', 'amateur', 'pro')),
    photo_url   TEXT,
    socials_json TEXT,
    email       VARCHAR(255),
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (nickname)
);

-- Events (tournaments)
CREATE TABLE IF NOT EXISTS events (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    date_start          DATE NOT NULL,
    date_end            DATE,
    city                VARCHAR(255) NOT NULL,
    level               VARCHAR(50) NOT NULL CHECK (level IN ('local', 'regional', 'national', 'international')),
    participants_count  INT,
    style               VARCHAR(50) CHECK (style IN ('street', 'park', 'universal')),
    has_best_trick      TINYINT(1) NOT NULL DEFAULT 0 CHECK (has_best_trick IN (0, 1)),
    source_url          TEXT,
    organizer_contact   TEXT,
    status              VARCHAR(50) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Results linking riders and events
CREATE TABLE IF NOT EXISTS results (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    event_id       INT NOT NULL,
    rider_id       INT NOT NULL,
    place          INT,
    is_finalist    TINYINT(1) NOT NULL DEFAULT 0 CHECK (is_finalist IN (0, 1)),
    is_participant TINYINT(1) NOT NULL DEFAULT 0 CHECK (is_participant IN (0, 1)),
    points         INT NOT NULL,
    comment        TEXT,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (rider_id) REFERENCES riders(id) ON DELETE CASCADE,
    UNIQUE (event_id, rider_id)
);

-- Cached rolling season points per rider
CREATE TABLE IF NOT EXISTS season_points (
    rider_id           INT PRIMARY KEY,
    season_points      INT NOT NULL DEFAULT 0,
    season_updated_at  TIMESTAMP NULL,
    FOREIGN KEY (rider_id) REFERENCES riders(id) ON DELETE CASCADE
);

-- Helpful indexes for common queries
CREATE INDEX IF NOT EXISTS idx_results_event_id ON results(event_id);
CREATE INDEX IF NOT EXISTS idx_results_rider_id ON results(rider_id);
CREATE INDEX IF NOT EXISTS idx_events_date_start ON events(date_start);
CREATE INDEX IF NOT EXISTS idx_riders_filters ON riders(city, level, style);

COMMIT;