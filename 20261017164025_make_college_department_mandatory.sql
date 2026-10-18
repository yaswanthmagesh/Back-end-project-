/*
# Make college_department a mandatory field

1. Modified Tables
- `registrations`
  - `college_department` column changed from nullable to NOT NULL
2. Security
- No RLS or policy changes.
3. Important Notes
- Existing rows with NULL college_department are updated to 'Unspecified' before
  the NOT NULL constraint is applied, so no data is lost.
- Future inserts MUST provide a college_department value.
*/

UPDATE registrations SET college_department = 'Unspecified' WHERE college_department IS NULL;

ALTER TABLE registrations ALTER COLUMN college_department SET NOT NULL;
