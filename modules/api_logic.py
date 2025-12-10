from flask import jsonify, request

def process_api_logic(req, db, config):

    cursor = db.cursor(dictionary=True)

    # ==========================
    # SI ES POST → ACCIÓN ADMIN
    # ==========================
    if req.method == "POST":
        data = req.get_json()
        action = data.get("action")
        session_id = data.get("session_id")

        if action == "clear_db":
            cursor.execute("DELETE FROM sessions")
            db.commit()
            return jsonify({"message": "DB limpiada"})

        cursor.execute("""
            UPDATE sessions SET action_request=%s
            WHERE id=%s
        """, (action, session_id))

        db.commit()
        return jsonify({"ok": True})

    # ==========================
    # SI ES GET → ESTADO CLIENTE
    # ==========================
    session_id = req.args.get("id")

    if session_id:
        cursor.execute("SELECT * FROM sessions WHERE id=%s", (session_id,))
        row = cursor.fetchone()
        return jsonify(row)

    cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    return jsonify(rows)
