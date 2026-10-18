# Event Registration Backend

A backend system that allows students to register for an event and lets organizers view all registrations. Built with **Python**, **Flask**, and **PostgreSQL** (via Supabase).

## Tech Stack

| Layer        | Technology             |
|-------------|------------------------|
| Language     | Python 3               |
| Framework    | Flask                  |
| Database     | PostgreSQL (Supabase)  |
| Validation   | Custom (server-side)   |

## Features

- Student event registration with a **50-participant capacity limit**
- Duplicate email prevention (checked at both application and database levels)
- College / Department is a mandatory field
- Server-side validation for all inputs
- Look up a single registration by UUID or email
- Built-in web interface for manual testing

## Project Structure

```
event-registration-backend/
├── app.py                            # Main server file (Flask app)
├── public/
│   └── index.html                    # Built-in testing interface
├── supabase/
│   └── migrations/
│       ├── 20261017161214_create_registrations_table.sql
│       └── 20261017164025_make_college_department_mandatory.sql
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variable template (safe to share)
├── .gitignore                        # Excludes node_modules, .env, and internal config
└── README.md
```

## API Endpoints

### 1. Register a Student

```
POST /register
```

**Request body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@college.edu",
  "college_department": "Computer Science"
}
```

| Field                | Required | Type   | Description                       |
|----------------------|----------|--------|-----------------------------------|
| name                 | Yes      | string | Student's full name               |
| email                | Yes      | string | Valid email, must be unique       |
| college_department   | Yes      | string | College or department (required)  |

**Success response (201):**
```json
{
  "message": "Registration successful.",
  "registration": {
    "id": "8e06b20f-68d6-428a-bdbf-bf5904ed47d7",
    "name": "Jane Doe",
    "email": "jane@college.edu",
    "college_department": "Computer Science",
    "registered_at": "2026-10-18T11:49:39+00:00"
  }
}
```

### 2. View All Registrations

```
GET /registrations
```

**Success response (200):**
```json
{
  "capacity": 50,
  "registered": 2,
  "seats_remaining": 48,
  "registrations": [ ... ]
}
```

### 3. View a Single Registration

```
GET /registrations/:identifier
```

The `:identifier` can be either a **registration UUID** or an **email address** — the API detects which one automatically.

**Success response (200):**
```json
{
  "registration": {
    "id": "8e06b20f-...",
    "name": "Jane Doe",
    "email": "jane@college.edu",
    "college_department": "Computer Science",
    "registered_at": "2026-10-18T11:49:39+00:00"
  }
}
```

### 4. Health Check

```
GET /health
```

**Success response (200):**
```json
{
  "status": "ok"
}
```

## Error Handling

| Scenario                    | Status Code | Error Message                        |
|----------------------------|-------------|--------------------------------------|
| Missing name               | 400         | `"Name is required."`               |
| Missing email              | 400         | `"Email is required."`              |
| Invalid email format       | 400         | `"A valid email is required."`      |
| Missing college/dept       | 400         | `"College / Department is required."` |
| Duplicate email            | 409         | `"This email is already registered."` |
| Event full (50 reached)    | 409         | `"Event is full."`                  |
| Registration not found     | 404         | `"Registration not found."`         |
| Server error               | 500         | `"Internal server error."`          |

## Capacity Management

The event has a maximum capacity of **50 participants**. Before each new registration, the server:

1. Checks if the email is already registered (returns 409 if duplicate)
2. Counts existing registrations and rejects new ones once the limit is reached (returns 409 if full)
3. Inserts the new registration with a unique constraint on `email` at the database level to prevent duplicates even under concurrent requests

## Setup

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- A [Supabase](https://supabase.com/) project (free tier works) OR any PostgreSQL database

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/event-registration-backend.git
   cd event-registration-backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Then fill in your Supabase (or PostgreSQL) connection details:
   ```
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   PORT=3000
   ```

5. Apply the database migrations to your Supabase project:
   - Go to the Supabase SQL Editor
   - Copy and run the SQL from `supabase/migrations/20261017161214_create_registrations_table.sql`
   - Then run the SQL from `supabase/migrations/20261017164025_make_college_department_mandatory.sql`

6. Start the server:
   ```bash
   python app.py
   ```

7. The server runs on `http://localhost:3000` (or the port you set).

## Database Schema

```
registrations
├── id                  (UUID, primary key, auto-generated)
├── name                (text, NOT NULL)
├── email               (text, UNIQUE, NOT NULL)
├── college_department  (text, NOT NULL)
└── registered_at       (timestamptz, defaults to now())
```

**Row Level Security (RLS)** is enabled with `anon, authenticated` policies for all CRUD operations, since this is a public registration API with no sign-in screen.

## Testing the API

You can test the endpoints using:

- **The browser interface** — open `http://localhost:3000` to use the built-in tester UI
- **cURL** —
  ```bash
  # Register a student
  curl -X POST http://localhost:3000/register \
    -H "Content-Type: application/json" \
    -d '{"name":"Jane Doe","email":"jane@college.edu","college_department":"Computer Science"}'

  # View all registrations
  curl http://localhost:3000/registrations

  # Look up by email
  curl http://localhost:3000/registrations/jane@college.edu
  ```
- **Postman** or any API client

### Test Scenarios

| Scenario                    | How to test                                      | Expected Response |
|----------------------------|--------------------------------------------------|-------------------|
| Successful registration    | POST with valid name, email, and college/dept    | 201 + record      |
| Duplicate registration     | POST the same email twice                        | 409 error         |
| Missing name               | POST without `name`                              | 400 error         |
| Missing email              | POST without `email`                             | 400 error         |
| Invalid email              | POST with `email: "notanemail"`                  | 400 error         |
| Missing college/dept       | POST without `college_department`                | 400 error         |
| Event full                 | Register 51 students                             | 409 error         |
| Registration not found     | GET a non-existent email or UUID                 | 404 error         |

## License

This project is for educational purposes.
