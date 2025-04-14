from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from auth import auth_bp
import re
import requests
import statistics
import models
import parser
from datetime import datetime
from draw_schedule import is_draw_day, is_draw_time, draw_schedules
from bs4 import BeautifulSoup
from scheduler import start_scheduler

# --- Initialize Flask App ---
app = Flask(__name__)
app.register_blueprint(auth_bp)
# scheduler = start_scheduler()
# --- Apply WSGI Middleware ---

# Reverse proxy support (e.g. when behind nginx or a load balancer)
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

# Extract prize breakdown table
# def extract_prize_table_data(soup):
#     prize_tables = soup.select('table.prizeBreakdownTable')
#     prize_data = []

#     for table in prize_tables:
#         rows = table.find_all('tr')[1:]
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) == 3:
#                 category = cols[0].get_text(strip=True)
#                 winners = cols[1].get_text(strip=True)
#                 prize = cols[2].get_text(strip=True)
#                 prize_data.append({
#                     'category': category,
#                     'winners': winners,
#                     'prize': prize
#                 })

#     return prize_data

# Extract prize + jackpot value from detail URL
# def get_prize_details_info(url):
#     html = get_page_contents(url)
#     if not html:
#         return {'error': 'Failed to fetch prize details'}
#     soup = BeautifulSoup(html, 'html.parser')

#     prize_data = extract_prize_table_data(soup)
#     jackpot = soup.select_one('.pastWinNumJackpot h3')
#     jackpot_value = jackpot.get_text(strip=True) if jackpot else None

#     if jackpot_value:
#         jackpot_value_cleaned = re.sub(r'[^\d]', '', jackpot_value)
#         jackpot_value = jackpot_value_cleaned

#     return prize_data, jackpot_value

# Parse main lottery result data from homepage
# def parse_lottery_html(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')
#     results = []

#     for tab in soup.select('.winNumTabContent'):
#         game_info = {}

#         title = tab.find('h2')
#         if not title:
#             continue
#         game_info['name'] = title.get_text(strip=True)

#         date = tab.find(class_='winNumHomeDate') or tab.find(class_='drawDate')
#         date_2 = date.get_text(strip=True) if date else 'Unknown'

#         try:
#             # Try parsing as "Friday, April 11, 2025"
#             formatted_date = datetime.strptime(date_2, "%A, %B %d, %Y").date()
#         except ValueError:
#             try:
#                 # Try parsing as "2025-04-11"
#                 formatted_date = datetime.strptime(date_2, "%Y-%m-%d").date()
#             except ValueError:
#                 raise ValueError(f"Unrecognized date format: {date_2}")
        
#         # parsed_date = datetime.strptime(date_2, "%A, %B %d, %Y")
#         # formatted_date = parsed_date.strftime("%Y-%m-%d")

#         game_info['date'] = formatted_date
#         main_numbers = tab.select('.winNumHomeNumber')
#         game_info['numbers'] = [num.get_text(strip=True) for num in main_numbers]

#         if not game_info['numbers']:
#             pick_numbers = tab.select('.winNumHomeNumberspick .winNumHomeNumber')
#             game_info['numbers'] = [num.get_text(strip=True) for num in pick_numbers]

#         bonus = tab.select_one('.winNumHomeNumberBonus, .winNumHomeNumberBonusDG')
#         if bonus:
#             bonus_text = bonus.get_text(strip=True).replace('Bonus', '').replace('GrandNumber', '').strip()
#             game_info['bonus'] = bonus_text
#         else:
#             game_info['bonus'] = None

#         extra = tab.select_one('.pastWinNumExtra')
#         if extra:
#             game_info['extra'] = extra.get_text(strip=True)

#         prize_details = tab.select('li.homePrizeDetails')
#         game_info['prize_details'] = [
#             'https://www.wclc.com' + li.get('rel') for li in prize_details if li.get('rel')
#         ]

#         # Handle "past winning numbers" link
#         past_winning_numbers = None
#         win_num_home_details = tab.select('li.winNumHomeDetail')
#         if len(win_num_home_details) >= 2:
#             onclick_value = win_num_home_details[1].get('onclick', None)
#             if onclick_value:
#                 past_winning_numbers = onclick_value.split("'")[1] if onclick_value else None

#         if past_winning_numbers:
#             game_info['past_winning_numbers'] = 'https://www.wclc.com' + past_winning_numbers
#         else:
#             game_info['past_winning_numbers'] = None

#         # Scrape each prize detail page
#         game_info['prize_details_data'] = []
#         for prize_url in game_info['prize_details']:
#             prize_data, jackpot_value = get_prize_details_info(prize_url)
#             game_info['jackpot_value'] = jackpot_value
#             game_info['prize_details_data'].append(prize_data)

            
# # Convert to normalized parsed structure


#         parsed = {
#             "date": game_info.get("date") ,  # "YYYY-MM-DD"
#             "name": game_info.get("name"),
#             "bonus": game_info.get("bonus"),
#             "extra": game_info.get("extra"),
#             "jackpot_value": int(game_info.get("jackpot_value") or 0),
#             "numbers": game_info.get("numbers", []),
#             "past_winning_numbers": game_info.get("past_winning_numbers", ""),
#             "prize_details": game_info.get("prize_details", []),
#             "prize_details_data": game_info.get("prize_details_data", []),
#         }

   

#         results.append(parsed)

#     return results



# --- Routes ---
# @app.route('/lottery')
# def lottery_route():
#     x = 1
#     #  if is_draw_day("lottoMax") and is_draw_time("lottoMax"):
#     url = 'https://www.wclc.com/home.htm'
#     page_contents = get_page_contents(url)

#     if not page_contents:
#         return '❌ Failed to retrieve lottery page.', 500

#     lotto_results = parse_lottery_html(page_contents)
#     return jsonify({'results': lotto_results})

# def get_data(condition, game):
#     if condition == 'noData':
 
#         url = 'https://www.wclc.com/home.htm'
#         page_contents = get_page_contents(url)

#         if not page_contents:
#             return '❌ Failed to retrieve Lotto Max statistics page.', 500
    
#         models.create_draw_tables()
#         lotto_results = parse_lottery_html(page_contents)
        

#         # parsed_frequencies = parser.parse_draw_result(lotto_results)

#         parsed_frequencies2 = parse_lottery_html(page_contents)

#         for draw in parsed_frequencies2:
#             models.save_draw_result(draw)
            

#         return jsonify({'data': parsed_frequencies2})
#         # models.create_draw_tables()
#         # cached_data = models.get_latest_draw('none')

#         # if not cached_data:
#         #     url = 'https://www.wclc.com/home.htm'
#         #     page_contents = get_page_contents(url)

#         #     if not page_contents:
#         #         return '❌ Failed to retrieve Lotto Max statistics page.', 500

#         #     lotto_results = parse_lottery_html(page_contents)
      


#         #     parsed_frequencies = parse_lottery_html(lotto_results)

#         #     for draw in parsed_frequencies:
#         #         models.save_draw_result(draw)
        
  

#         # return jsonify({'data': cached_data})
    
#     if condition == 'hasData':
#         models.create_draw_tables()
#         cached_data = models.get_latest_draw(game)

#         if not cached_data:
#             url = 'https://www.wclc.com/home.htm'
#             page_contents = get_page_contents(url)

#             if not page_contents:
#                 return '❌ Failed to retrieve Lotto Max statistics page.', 500

#             lotto_results = parse_lottery_html(page_contents)
      


#             parsed_frequencies = parser.parse_draw_result(lotto_results)

#             for draw in parsed_frequencies:
#                 models.save_draw_result(draw)
        
  

#         return jsonify({'data': cached_data})
  


@app.route('/lottery')
def lottery_route():

    results = models.get_latest_draw('latest')
    return jsonify({'results': results})
     # TODO: this function must be filter propertly, and include the save to database the prize_details_data

    # if x == 1: 
    #     url = 'https://www.wclc.com/home.htm'
    #     page_contents = get_page_contents(url)

    #     if not page_contents:
    #         return '❌ Failed to retrieve Lotto Max statistics page.', 500
        
    #     models.create_draw_tables()
    #     lotto_results = parse_lottery_html(page_contents)
      

    #     # parsed_frequencies = parser.parse_draw_result(lotto_results)

    #     parsed_frequencies2 = parse_lottery_html(page_contents)

    #     for draw in parsed_frequencies2:
    #         models.save_draw_result(draw)
            

    #     return jsonify({'data': parsed_frequencies2})

    # else:
    #     models.create_draw_tables()
    #     cached_data = models.get_latest_draw()

    #     if not cached_data:
    #         url = 'https://www.wclc.com/home.htm'
    #         page_contents = get_page_contents(url)

    #         if not page_contents:
    #             return '❌ Failed to retrieve Lotto Max statistics page.', 500

    #         lotto_results = parse_lottery_html(page_contents)
      


    #         parsed_frequencies = parser.parse_draw_result(lotto_results)

    #         for draw in parsed_frequencies:
    #             models.save_draw_result(draw)
        
  

    #     return jsonify({'data': cached_data})

    # url = 'https://www.wclc.com/home.htm'
    # page_contents = get_page_contents(url)

    # if not page_contents:
    #     return '❌ Failed to retrieve lottery page.', 500

    # lotto_results = parse_lottery_html(page_contents)
    # return jsonify({'results': lotto_results})

@app.route('/statistics')
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

    # else:
    #     models.create_tables()
    #     cached_data = models.get_latest_frequencies()

    #     if not cached_data:
    #         return '⚠️ No cached data available yet. Please check back during draw time.', 404

    #     return jsonify({'data': cached_data})



# --- Run the App ---
if __name__ == "__main__":
    start_scheduler()  # Start scheduler in the background
    app.run(host='127.0.0.1', port=5000, debug=True)

# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=5000, debug=True)
