PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    service_name TEXT NOT NULL,
    project_name TEXT NOT NULL,
    client_name TEXT,
    project_status TEXT,
    priority TEXT NOT NULL DEFAULT 'Medium',
    owner TEXT NOT NULL,
    start_date TEXT,
    due_date TEXT,
    contact_number TEXT,
    remark TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects (owner);
CREATE INDEX IF NOT EXISTS idx_projects_priority ON projects (priority);
CREATE INDEX IF NOT EXISTS idx_projects_due_date ON projects (due_date);
CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects (updated_at);

CREATE TABLE IF NOT EXISTS actions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    action_name TEXT NOT NULL,
    description TEXT,
    action_status TEXT NOT NULL DEFAULT 'Not Started',
    priority TEXT NOT NULL DEFAULT 'Medium',
    assignee TEXT,
    start_date TEXT,
    due_date TEXT,
    progress_percent INTEGER NOT NULL DEFAULT 0,
    remark TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_actions_project_id ON actions (project_id);
CREATE INDEX IF NOT EXISTS idx_actions_status ON actions (action_status);
CREATE INDEX IF NOT EXISTS idx_actions_priority ON actions (priority);
CREATE INDEX IF NOT EXISTS idx_actions_assignee ON actions (assignee);
CREATE INDEX IF NOT EXISTS idx_actions_due_date ON actions (due_date);
CREATE INDEX IF NOT EXISTS idx_actions_updated_at ON actions (updated_at);

CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    action_id TEXT,
    comment_text TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_comments_project_id ON comments (project_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments (created_at);

CREATE TABLE IF NOT EXISTS activity_logs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    action_id TEXT,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    updated_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    comment TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_project_id ON activity_logs (project_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action_id ON activity_logs (action_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_updated_at ON activity_logs (updated_at);
