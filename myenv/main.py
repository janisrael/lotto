from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from auth import auth_bp
from auth_middleware import token_required  # Import the token_required decorator
import requests
import models
from cron import run_lottery_job
import statistics
import parser
from datetime import datetime
# from draw_schedule import is_draw_day, is_draw_time, draw_schedules
from bs4 import BeautifulSoup
from scheduler import start_scheduler



# --- Initialize Flask App ---
app = Flask(__name__)
app.register_blueprint(auth_bp, url_prefix='/auth')  # Register auth blueprint

# --- Apply WSGI Middleware ---
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

# Custom logger middleware (logs each request)
class SimpleLoggerMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get('REQUEST_METHOD')
        path = environ.get('PATH_INFO')
        print(f"[LOG] {method} {path}")
        return self.app(environ, start_response)

# Apply the logger middleware
app.wsgi_app = SimpleLoggerMiddleware(app.wsgi_app)

# --- Utilities ---

# Fetch HTML page
def get_page_contents(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


@app.route('/lottery')
# @token_required  # Protect this route with token_required middleware
def lottery_route():
    # results = models.get_latest_draw('latest')
    results = run_lottery_job('lotto649')
    return jsonify({'results': results})


@app.route('/statistics')
@token_required  # Protect this route with token_required middleware
def statistics_route():
    # if is_draw_day("lottoMax") and is_draw_time("lottoMax"):
    url = 'https://www.lottomaxnumbers.com/statistics'
    page_contents = get_page_contents(url)

    if not page_contents:
        return '❌ Failed to retrieve Lotto Max statistics page.', 500

    models.create_tables()
    lotto_frequencies = statistics.parse_lotto_max_frequencies(page_contents)
    parsed_frequencies = parser.parse_lotto_max_frequencies(lotto_frequencies)
    models.save_frequencies(parsed_frequencies)

    return jsonify({'data': parsed_frequencies})

# --- Run the App ---
if __name__ == "__main__":
    # start_scheduler()  # Start scheduler in the background
    app.run(host='127.0.0.1', port=5001, debug=True)
