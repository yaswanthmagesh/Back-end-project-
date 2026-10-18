/*
# Create registrations table for student event registration

1. New Tables
- `registrations`
  - `id` (uuid, primary key, auto-generated)
  - `name` (text, not null) — student's full name
  - `email` (text, unique, not null) — student's email, used for duplicate detection
  - `college_department` (text, nullable) — optional college or department
  - `registered_at` (timestamptz, default now()) — registration timestamp
2. Security
- Enable RLS on `registrations`.
- Allow anon + authenticated CRUD because this is a no-auth public registration API
  (no sign-in screen — the backend API is open for registration and viewing).
3. Important Notes
- The 50-participant capacity limit is enforced at the application layer
  by counting existing rows before each insert.
- Email uniqueness is enforced at the database level via a UNIQUE constraint
  to prevent duplicate registrations even under concurrent requests.
- An index on `email` supports fast duplicate checks and lookups.
*/

CREATE TABLE IF NOT EXISTS registrations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  email text UNIQUE NOT NULL,
  college_department text,
  registered_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE registrations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "anon_select_registrations" ON registrations;
CREATE POLICY "anon_select_registrations" ON registrations FOR SELECT
  TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_registrations" ON registrations;
CREATE POLICY "anon_insert_registrations" ON registrations FOR INSERT
  TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_registrations" ON registrations;
CREATE POLICY "anon_update_registrations" ON registrations FOR UPDATE
  TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_registrations" ON registrations;
CREATE POLICY "anon_delete_registrations" ON registrations FOR DELETE
  TO anon, authenticated USING (true);