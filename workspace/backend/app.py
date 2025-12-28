

from flask import Flask


from views.api import api
from views.billing import billing
from views.subscription import subscription
from views.webhook import webhook

from views.docs import docs
from views.notifications_api import notifications_api


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambia esto en producción
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(billing)
app.register_blueprint(subscription)
app.register_blueprint(webhook)
app.register_blueprint(docs)
app.register_blueprint(notifications_api)

if __name__ == '__main__':
    app.run(debug=True)
