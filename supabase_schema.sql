-- Enable the pgcrypto extension to allow UUID generation
create extension if not exists "pgcrypto";

-- PROJECTS TABLE
create table if not exists projects (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  description text,
  start_date date,
  deadline date,
  parent_company text,
  business_partner text,
  team_members jsonb, -- List of employee IDs or names
  milestones jsonb,   -- List of milestone objects
  current_progress float default 0.0,
  status_updates jsonb,
  budget float,
  actual_spend float default 0.0,
  created_at timestamp with time zone default now()
);

-- EMPLOYEES TABLE
create table if not exists employees (
  id text primary key, -- Keeping as text to match potential CSV IDs easily, or could be UUID
  name text not null,
  role text,
  department text,
  join_date date,
  performance_ratings jsonb,
  projects_history jsonb,
  attendance_record jsonb,
  skills text[], -- Array of text
  certifications jsonb,
  created_at timestamp with time zone default now()
);

-- FINANCIAL RECORDS TABLE
create table if not exists financial_records (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references projects(id) on delete cascade,
  date date not null,
  category text,
  amount float not null,
  description text,
  approved_by text,
  budget_category text,
  created_at timestamp with time zone default now()
);

-- CHAT HISTORY TABLE
create table if not exists chat_history (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references projects(id) on delete cascade,
  message text not null,
  response text,
  timestamp timestamp with time zone default now()
);
