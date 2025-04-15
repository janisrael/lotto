
import models
from flask import jsonify
# import parser
import re
import requests
import models
from parser.lotto_result_parser import parse_lm_result,parse_649_result
from datetime import datetime
from bs4 import BeautifulSoup
from config import SOURCE_DATA
# from main import get_page_contents, parse_lottery_html

# Fetch HTML page
def get_page_contents(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None

# Parse main lottery result data from homepage
def parse_lottery_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []

    for tab in soup.select('.winNumTabContent'):
        game_info = {}

        title = tab.find('h2')
        if not title:
            continue
        game_info['name'] = title.get_text(strip=True)

        date = tab.find(class_='winNumHomeDate') or tab.find(class_='drawDate')
        date_2 = date.get_text(strip=True) if date else 'Unknown'

        try:
            # Try parsing as "Friday, April 11, 2025"
            formatted_date = datetime.strptime(date_2, "%A, %B %d, %Y").date()
        except ValueError:
            try:
                # Try parsing as "2025-04-11"
                formatted_date = datetime.strptime(date_2, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Unrecognized date format: {date_2}")
        
        # parsed_date = datetime.strptime(date_2, "%A, %B %d, %Y")
        # formatted_date = parsed_date.strftime("%Y-%m-%d")

        game_info['date'] = formatted_date
        main_numbers = tab.select('.winNumHomeNumber')
        game_info['numbers'] = [num.get_text(strip=True) for num in main_numbers]

        if not game_info['numbers']:
            pick_numbers = tab.select('.winNumHomeNumberspick .winNumHomeNumber')
            game_info['numbers'] = [num.get_text(strip=True) for num in pick_numbers]

        bonus = tab.select_one('.winNumHomeNumberBonus, .winNumHomeNumberBonusDG')
        if bonus:
            bonus_text = bonus.get_text(strip=True).replace('Bonus', '').replace('GrandNumber', '').strip()
            game_info['bonus'] = bonus_text
        else:
            game_info['bonus'] = None

        extra = tab.select_one('.pastWinNumExtra')
        if extra:
            game_info['extra'] = extra.get_text(strip=True)

        prize_details = tab.select('li.homePrizeDetails')
        game_info['prize_details'] = [
            SOURCE_DATA + li.get('rel') for li in prize_details if li.get('rel')
        ]

        # Handle "past winning numbers" link
        past_winning_numbers = None
        win_num_home_details = tab.select('li.winNumHomeDetail')
        if len(win_num_home_details) >= 2:
            onclick_value = win_num_home_details[1].get('onclick', None)
            if onclick_value:
                past_winning_numbers = onclick_value.split("'")[1] if onclick_value else None

        if past_winning_numbers:
            game_info['past_winning_numbers'] = SOURCE_DATA + past_winning_numbers
        else:
            game_info['past_winning_numbers'] = None

        # Scrape each prize detail page
        game_info['prize_details_data'] = []
        for prize_url in game_info['prize_details']:
            prize_data, jackpot_value = get_prize_details_info(prize_url)
            game_info['jackpot_value'] = jackpot_value
            game_info['prize_details_data'].append(prize_data)

            
# Convert to normalized parsed structure


        parsed = {
            "date": game_info.get("date") ,  # "YYYY-MM-DD"
            "name": game_info.get("name"),
            "bonus": game_info.get("bonus"),
            "extra": game_info.get("extra"),
            "jackpot_value": int(game_info.get("jackpot_value") or 0),
            "numbers": game_info.get("numbers", []),
            "past_winning_numbers": game_info.get("past_winning_numbers", ""),
            "prize_details": game_info.get("prize_details", []),
            "prize_details_data": game_info.get("prize_details_data", []),
        }

   

        results.append(parsed)

    return results

# Extract prize breakdown table
def extract_prize_table_data(soup):
    prize_tables = soup.select('table.prizeBreakdownTable')
    prize_data = []

    for table in prize_tables:
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 3:
                category = cols[0].get_text(strip=True)
                winners = cols[1].get_text(strip=True)
                prize = cols[2].get_text(strip=True)
                prize_data.append({
                    'category': category,
                    'winners': winners,
                    'prize': prize
                })

    return prize_data

# Extract prize + jackpot value from detail URL
def get_prize_details_info(url):
    html = get_page_contents(url)
    if not html:
        return {'error': 'Failed to fetch prize details'}
    soup = BeautifulSoup(html, 'html.parser')

    prize_data = extract_prize_table_data(soup)
    jackpot = soup.select_one('.pastWinNumJackpot h3')
    jackpot_value = jackpot.get_text(strip=True) if jackpot else None

    if jackpot_value:
        jackpot_value_cleaned = re.sub(r'[^\d]', '', jackpot_value)
        jackpot_value = jackpot_value_cleaned

    return prize_data, jackpot_value


def run_lottery_job(draw_name):
    # from main import get_page_contents, parse_lottery_html  # delayed import

    # for game_id: LM /winning-numbers/lotto-max-extra.htm
    print('running')
    example = []
    if draw_name.lower() == 'lottomax':
        games = [
            {
                "game_id": "LM",
                "url": SOURCE_DATA + '/winning-numbers/lotto-max-extra.htm',
                "game_name": 'LOTTO MAX'
            },
            {
                "game_id": "WM",
                "url": SOURCE_DATA + '/winning-numbers/western-max-extra.htm',
                "game_name": 'LOTTO MAX WESTERN'
            }
        ]

    
        for game in games:
            page_contents = get_page_contents(game["url"])

            if not page_contents:
                return f'❌ Failed to retrieve data for {game["game_name"]}.', 500

            models.create_draw_tables()

            # Parse result (same parser for both)
            parsed_data = parse_lm_result(page_contents, game)
            example.append(parsed_data)
            # # Save parsed data
            for draw in parsed_data:
                models.save_dra_lm_result(draw, game)

    if draw_name.lower() == 'lotto649':
        games = [
            {
                "game_id": "6-49",
                "url": SOURCE_DATA + '/winning-numbers/lotto-649-extra.htm',
                "game_name": 'LOTTO 6-49'
            },
            {
                "game_id": "W6-49",
                "url": SOURCE_DATA + '/winning-numbers/western-649-extra.htm',
                "game_name": 'LOTTO 6-49 WESTERN'
            }
        ]

    
        for game in games:
            page_contents = get_page_contents(game["url"])

            if not page_contents:
                return f'❌ Failed to retrieve data for {game["game_name"]}.', 500

            models.create_draw_tables()

            # Parse result (same parser for both)
            parsed_data = parse_649_result(page_contents, game)
            
            example.append(parsed_data)
            # # Save parsed data
            for draw in parsed_data:
                models.save_dra_649_result(draw, game)

    return example