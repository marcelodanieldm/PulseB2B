from flask import Blueprint, jsonify
from collections import Counter

user_stats_api = Blueprint('user_stats_api', __name__)

# Simulación de usuarios (reemplazar por DB real)
USERS = [
    {'id': 1, 'plan_type': 'free', 'country': 'AR', 'services': ['Webhooks']},
    {'id': 2, 'plan_type': 'pro', 'country': 'MX', 'services': ['Webhooks', 'API']},
    {'id': 3, 'plan_type': 'enterprise', 'country': 'CO', 'services': ['API', 'Slack', 'HubSpot']},
    {'id': 4, 'plan_type': 'pro', 'country': 'AR', 'services': ['Slack']},
    {'id': 5, 'plan_type': 'free', 'country': 'ES', 'services': []},
    {'id': 6, 'plan_type': 'free', 'country': 'US', 'services': ['API']},
    {'id': 7, 'plan_type': 'enterprise', 'country': 'MX', 'services': ['Webhooks', 'API', 'Slack']},
    # ... más usuarios
]

@user_stats_api.route('/api/admin/user-stats', methods=['GET'])
def get_user_stats():
    free = [u for u in USERS if u['plan_type'] == 'free']
    pro = [u for u in USERS if u['plan_type'] == 'pro']
    enterprise = [u for u in USERS if u['plan_type'] == 'enterprise']
    # Servicios
    all_services = [s for u in USERS for s in u['services']]
    services_count = dict(Counter(all_services))
    # Países
    all_countries = [u['country'] for u in USERS]
    countries_count = dict(Counter(all_countries))
    return jsonify({
        'freeCount': len(free),
        'proCount': len(pro),
        'enterpriseCount': len(enterprise),
        'usersByService': services_count,
        'usersByCountry': countries_count
    })
