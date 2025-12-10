from flask import request, redirect

def block_ip_if_needed(config):
    ip_block_file = config["ip_block_file"]

    # Leer IP bloqueadas
    try:
        with open(ip_block_file, "r") as f:
            blocked_ips = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        blocked_ips = []

    client_ip = request.remote_addr

    if client_ip in blocked_ips:
        return redirect("https://www.google.com")  # igual que PHP

    return None
