CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    kpi_category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'start',
    priority TEXT NOT NULL DEFAULT 'Medium',
    assignee TEXT,
    owner TEXT,
    contact_number TEXT,
    department TEXT,
    progress_percent TEXT,
    tags TEXT,
    stage TEXT,
    due_date TEXT,
    next_step TEXT,
    issue TEXT,
    current_status TEXT,
    last_update TEXT,
    internal_action TEXT,
    client_feedback TEXT,
    company_name TEXT,
    requested_date TEXT,
    industry TEXT,
    x_number_total TEXT,
    x_number_range TEXT,
    business_scenario TEXT,
    fit_level TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_kpi_category ON tasks (kpi_category);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks (updated_at);

CREATE TABLE IF NOT EXISTS timeline_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    update_title TEXT,
    update_type TEXT,
    priority TEXT,
    description TEXT,
    related_status TEXT,
    created_by TEXT,
    attachment_url TEXT,
    stage_label TEXT NOT NULL,
    status_label TEXT NOT NULL,
    update_note TEXT NOT NULL,
    start_date TEXT,
    due_date TEXT,
    update_date TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_timeline_updates_task_id ON timeline_updates (task_id);
CREATE INDEX IF NOT EXISTS idx_timeline_updates_created_at ON timeline_updates (created_at);
