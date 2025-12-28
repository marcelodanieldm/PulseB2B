from flask import Blueprint, jsonify, request
from datetime import datetime

notifications_api = Blueprint('notifications_api', __name__)

# Simulación de almacenamiento en memoria (reemplazar por DB en producción)
NOTIFICATIONS = []

@notifications_api.route('/api/admin/notifications', methods=['GET'])
def get_notifications():
    """
    Devuelve las notificaciones recientes de nuevos usuarios Pro y desuscripciones.
    Query params:
      - type: 'pro' | 'unsub' | None (ambos)
      - limit: int (default 20)
    """
    notif_type = request.args.get('type')
    limit = int(request.args.get('limit', 20))
    filtered = [n for n in NOTIFICATIONS if notif_type in (None, '', n['type']) or notif_type is None]
    return jsonify(filtered[-limit:][::-1])

# Utilidad para agregar notificaciones (llamar desde Stripe webhook y unsubscribe)
def add_notification(type_, name, email, ip, country):
    NOTIFICATIONS.append({
        'id': len(NOTIFICATIONS) + 1,
        'type': type_,  # 'pro' o 'unsub'
        'name': name,
        'email': email,
        'ip': ip,
        'country': country,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M')
    })

# Ejemplo de uso:
# add_notification('pro', 'Ana Pro', 'ana@pro.com', '190.1.2.3', 'AR')
# add_notification('unsub', 'Carlos Free', 'carlos@free.com', '181.3.4.5', 'CO')
