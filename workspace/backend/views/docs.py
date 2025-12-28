from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
import datetime

docs = Blueprint('docs', __name__)

# RBAC-protected API docs route
@docs.route('/docs/api')
def api_docs():
    user = session.get('user')
    access_log = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'ip': request.remote_addr,
        'user': user['username'] if user else None,
        'plan_type': user['plan_type'] if user else None
    }
    # Log access attempt (could be saved to DB or file)
    print('[DOCS ACCESS]', access_log)

    if not user:
        # Not logged in: redirect to login or show locked page
        return render_template('locked_docs.html', reason='not_logged_in')
    if user.get('plan_type') == 'enterprise':
        # Enterprise: show full docs
        return render_template('api_docs.html', user=user)
    # Free/Pro: show gated/locked UX
    return render_template('locked_docs.html', reason=user.get('plan_type'))
