from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix
from auth import auth_bp
from auth_middleware import token_required  # Import the token_required decorator
import requests
from models.save_data import *
from models.get_data import get_latest_draw,get_past_draw
from cron import run_lottery_job
import statistics
import parser
from datetime import datetime
# from draw_schedule import is_draw_day, is_draw_time, draw_schedules
from bs4 import BeautifulSoup
from scheduler import start_scheduler
from flask_cors import CORS


# --- Initialize Flask App ---
app = Flask(__name__)
# For Development (Allow all origins)
CORS(app, origins="*")

# For Production (Restrict to specific frontend domain)
CORS(app, origins=["http://localhost:8080", "https://your-production-domain.com"])


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


# Fetch HTML page
def get_page_contents(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None

@app.route('/latest')
# @token_required  # Protect this route with token_required middleware
def latest_route():
    results = get_latest_draw('all')
    # results = run_lottery_job('dailygrand')
    return jsonify({'latest_draw_data': results})


@app.route('/lottery')
# @token_required  # Protect this route with token_required middleware
def lottery_route():
    results = get_latest_draw('all')
    # results = run_lottery_job('dailygrand')
    return jsonify({'results': results})

@app.route('/past-results', methods=['GET'])
# @token_required
def past_results_route():
    data = request.get_json()

    game_id = data.get('game_id')  # safely get game_id
    start_date = data.get('start_date')  # optional
    end_date = data.get('end_date')      # optional

    if not game_id:
        return jsonify({'error': 'game_id is required'}), 400

    results = get_past_draw(game_id=game_id, start_date=start_date, end_date=end_date)
    return jsonify({'results': results})


@app.route('/statistics')
@token_required  # Protect this route with token_required middleware
def statistics_route():
    # if is_draw_day("lottoMax") and is_draw_time("lottoMax"):
    url = 'https://www.lottomaxnumbers.com/statistics'
    page_contents = get_page_contents(url)

    if not page_contents:
        return '❌ Failed to retrieve Lotto Max statistics page.', 500

    create_tables()
    lotto_frequencies = statistics.parse_lotto_max_frequencies(page_contents)
    parsed_frequencies = parser.parse_lotto_max_frequencies(lotto_frequencies)
    save_frequencies(parsed_frequencies)

    return jsonify({'data': parsed_frequencies})

# --- Run the App ---
if __name__ == "__main__":
    start_scheduler()  # Start scheduler in the background
    app.run(host='127.0.0.1', port=5001, debug=True)
