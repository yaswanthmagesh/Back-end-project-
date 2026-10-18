import os
import re
from flask import Flask, request, jsonify, send_from_directory
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="public", static_url_path="")

PORT = int(os.environ.get("PORT", 3000))
MAX_CAPACITY = 50

supabase_url = os.environ.get("VITE_SUPABASE_URL")
supabase_anon_key = os.environ.get("VITE_SUPABASE_ANON_KEY")

if not supabase_url or not supabase_anon_key:
    print("Missing Supabase environment variables. Check your .env file.")
    raise SystemExit(1)

supabase: Client = create_client(supabase_url, supabase_anon_key)

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(email):
    return bool(EMAIL_REGEX.match(email))


@app.route("/")
def index():
    return send_from_directory("public", "index.html")


@app.post("/register")
def register():
    try:
        body = request.get_json(silent=True) or {}
        name = body.get("name")
        email = body.get("email")
        college_department = body.get("college_department")

        if not name or not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Name is required."}), 400
        if not email or not isinstance(email, str) or not email.strip():
            return jsonify({"error": "Email is required."}), 400
        if not is_valid_email(email.strip()):
            return jsonify({"error": "A valid email is required."}), 400
        if not college_department or not isinstance(college_department, str) or not college_department.strip():
            return jsonify({"error": "College / Department is required."}), 400

        normalized_email = email.strip().lower()
        clean_name = name.strip()
        clean_dept = college_department.strip()

        existing = (
            supabase.table("registrations")
            .select("id")
            .eq("email", normalized_email)
            .maybe_single()
            .execute()
        )

        if existing is not None:
            return jsonify({"error": "This email is already registered."}), 409

        count_resp = (
            supabase.table("registrations")
            .select("*", count="exact")
            .execute()
        )

        count = count_resp.count if count_resp.count is not None else 0

        if count >= MAX_CAPACITY:
            return jsonify({
                "error": "Event is full.",
                "capacity": MAX_CAPACITY,
                "registered": count,
            }), 409

        insert_resp = (
            supabase.table("registrations")
            .insert({
                "name": clean_name,
                "email": normalized_email,
                "college_department": clean_dept,
            })
            .select()
            .single()
            .execute()
        )

        if not insert_resp.data:
            print("Insert failed: no data returned")
            return jsonify({"error": "Could not complete registration."}), 500

        return jsonify({
            "message": "Registration successful.",
            "registration": insert_resp.data,
        }), 201

    except Exception as err:
        err_str = str(err)
        if "23505" in err_str:
            return jsonify({"error": "This email is already registered."}), 409
        print(f"Unexpected error in /register: {err}")
        return jsonify({"error": "Internal server error."}), 500


@app.get("/registrations")
def get_all_registrations():
    try:
        resp = (
            supabase.table("registrations")
            .select("*", count="exact")
            .order("registered_at", desc=False)
            .execute()
        )

        count = resp.count if resp.count is not None else 0

        return jsonify({
            "capacity": MAX_CAPACITY,
            "registered": count,
            "seats_remaining": max(0, MAX_CAPACITY - count),
            "registrations": resp.data,
        }), 200

    except Exception as err:
        print(f"Unexpected error in /registrations: {err}")
        return jsonify({"error": "Internal server error."}), 500


@app.get("/registrations/<path:identifier>")
def get_single_registration(identifier):
    try:
        if "@" in identifier:
            query = (
                supabase.table("registrations")
                .select("*")
                .eq("email", identifier.lower())
            )
        else:
            query = (
                supabase.table("registrations")
                .select("*")
                .eq("id", identifier)
            )

        resp = query.maybe_single().execute()

        if resp is None or not resp.data:
            return jsonify({
                "error": "Registration not found.",
                "identifier": identifier,
            }), 404

        return jsonify({"registration": resp.data}), 200

    except Exception as err:
        print(f"Unexpected error in /registrations/<identifier>: {err}")
        return jsonify({"error": "Internal server error."}), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
