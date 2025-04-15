import models
from flask import jsonify
# import parser
import re
import requests
import models
from datetime import datetime
from bs4 import BeautifulSoup
from config import SOURCE_DATA

from bs4 import BeautifulSoup


# Fetch HTML page
def get_page_contents(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


def parse_lm_result(html, game):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Initialize an empty list to store the draw data
    draw_data = []

    # Game Type
    game_type = game["game_name"]

    # Loop through each draw
    for draw in soup.select('div.pastWinNum'):
        # Extract draw date
        date_tag = draw.select_one('div.pastWinNumDate h4')
        draw_date = date_tag.get_text(strip=True) if date_tag else None

        try:
            # Try parsing as "Friday, April 11, 2025"
            formatted_date = datetime.strptime(draw_date, "%A, %B %d, %Y").date()
        except ValueError:
            try:
                # Try parsing as "2025-04-11"
                formatted_date = datetime.strptime(draw_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Unrecognized date format: {draw_date}")
            

        # Extract winning numbers
        numbers = [li.get_text(strip=True) for li in draw.select('li.pastWinNumber')]
        
        # Extract bonus number
        bonus_tag = draw.select_one('li.pastWinNumberBonus')
        bonus = bonus_tag.get_text(strip=True).replace("Bonus", "").strip() if bonus_tag else None

        # Extract extra number
        extra_tag = draw.select_one('div.pastWinNumExtra')
        extra_number = extra_tag.get_text(strip=True) if extra_tag else None

        # Extract draw number from the prize breakdown link
        prize_breakdown = draw.select_one('div.pastWinNumPrizeBreakdown')
        draw_number = None
        prize_break_down = None  # Initialize the prize breakdown variable
        if prize_breakdown and 'rel' in prize_breakdown.attrs:
            rel = prize_breakdown['rel']
            prize_break_down = rel  # Assign the rel value to the prize_break_down property
            if "drawNumber=" in rel:
                draw_number = rel.split('drawNumber=')[-1]

        # Extract MAXMILLIONS numbers (if any)
        maxmillions_draws = []
        for ul in draw.select('div.pastWinNumMMGroup ul.pastWinNumbers'):
            mm_numbers = [li.get_text(strip=True) for li in ul.select('li.pastWinNumMM')]
            if mm_numbers:
                maxmillions_draws.append(mm_numbers)

        # Get prize breakdown
        prize_breakdown_data, jackpot_value = get_prize_details_info(SOURCE_DATA + prize_break_down)

        # Append the parsed data for each draw to the list
        draw_data.append({
            'date': formatted_date,
            'draw_number': draw_number,
            'name': game_type,
            'numbers': numbers,
            'jackpot_value': jackpot_value,
            'bonus': bonus,
            'extra': extra_number,
            'maxmillions': maxmillions_draws,
            'prize_break_down': prize_break_down,
            'prize_details_data': prize_breakdown_data
        })

    return draw_data



# Extract prize + jackpot value from detail URL
def get_prize_details_info_649(url):
    html = get_page_contents(url)
    if not html:
        return {'error': 'Failed to fetch prize details'}
    soup = BeautifulSoup(html, 'html.parser')

    prize_data = extract_prize_table_649_data(soup)
    jackpot = soup.select_one('.pastWinNumJackpot h3')
    jackpot_value = jackpot.get_text(strip=True) if jackpot else None

    if jackpot_value:
        jackpot_value_cleaned = re.sub(r'[^\d]', '', jackpot_value)
        jackpot_value = jackpot_value_cleaned

    return prize_data, jackpot_value

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

def extract_prize_table_649_data(soup):
    prize_tables = soup.select('table.prizeBreakdownTable')
    prize_data = []
    extra_price_breakdown = []

    for i, table in enumerate(prize_tables):
        rows = table.find_all('tr')[1:]  # Skipping header row
        current_table_data = []

        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 3:
                category = cols[0].get_text(strip=True)
                winners = cols[1].get_text(strip=True)
                prize = cols[2].get_text(strip=True)
                current_table_data.append({
                    'category': category,
                    'winners': winners,
                    'prize': prize
                })

        # Only collect prize data from the FIRST table
        if i == 0:
            prize_data = current_table_data
        # If SUPER DRAWS is not found, the LAST table becomes the extra breakdown
        elif i == len(prize_tables) - 1:
            extra_price_breakdown = current_table_data

    # Parsing Gold Ball Draw
    gold_ball = soup.select_one('div.pastWinNumLogoGPD')
    gold_ball_info = {
        'ball': gold_ball.get_text(strip=True) if gold_ball else 'N/A',
        'winners': []
    }

    # Gold ball table is usually the second table, if it exists
    if len(prize_tables) > 1:
        gold_ball_table = prize_tables[1]  # The second table
        gold_ball_rows = gold_ball_table.find_all('tr')[1:]  # Skipping header row
        for row in gold_ball_rows:
            cols = row.find_all('td')
            if len(cols) == 3:
                winning_number = cols[0].get_text(strip=True)
                winners = cols[1].get_text(strip=True)
                prize = cols[2].get_text(strip=True)
                gold_ball_info['winners'].append({
                    'winning_number': winning_number,
                    'winners': winners,
                    'prize': prize
                })
    super_draws_header = soup.find('h3', string=lambda text: text and 'SUPER DRAWS' in text.upper())
    su_d = None
    super_draws = []
    if super_draws_header:
         # Parsing Super Draws

        if len(prize_tables) > 2:
            super_draw_table = prize_tables[2]  # Super draws are in the third table
            super_draw_rows = super_draw_table.find_all('tr')[1:]  # Skipping header row
            for row in super_draw_rows:
                cols = row.find_all('td')
                if len(cols) == 3:
                    winning_number = cols[0].get_text(strip=True)
                    winners = cols[1].get_text(strip=True)
                    prize = cols[2].get_text(strip=True)
                    super_draws.append({
                        'winning_number': winning_number,
                        'winners': winners,
                        'prize': prize
                    })
   

    # Return the parsed data
    return {
        'prize_data': prize_data,
        'extra_price_breakdown': extra_price_breakdown,
        'gold_ball_drawn': gold_ball_info,
        'super_draws': super_draws
    }


# Extract prize breakdown table
def extract_prize_table_data(soup):
   
    prize_tables = soup.select('table.prizeBreakdownTable')
    prize_data = []
    extra_price_breakdown = []

    for i, table in enumerate(prize_tables):
        rows = table.find_all('tr')[1:]
        current_table_data = []

        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 3:
                category = cols[0].get_text(strip=True)
                winners = cols[1].get_text(strip=True)
                prize = cols[2].get_text(strip=True)
                current_table_data.append({
                    'category': category,
                    'winners': winners,
                    'prize': prize
                })

        if i == len(prize_tables) - 1:
            extra_price_breakdown = current_table_data
        else:
            prize_data.extend(current_table_data)

    return {
        'prize_data': prize_data,
        'extra_price_breakdown': extra_price_breakdown
    }



# 6-49

def parse_649_result(html, game):
    soup = BeautifulSoup(html, 'html.parser')
    draw_data = []

    game_type = game["game_name"]

    for draw in soup.select('div.pastWinNum'):
        # Extract draw date
        date_tag = draw.select_one('div.pastWinNumDate h4')
        draw_date = date_tag.get_text(strip=True) if date_tag else None

        try:
            formatted_date = datetime.strptime(draw_date, "%A, %B %d, %Y").date()
        except ValueError:
            try:
                formatted_date = datetime.strptime(draw_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Unrecognized date format: {draw_date}")

        # Extract winning numbers
        numbers = [li.get_text(strip=True) for li in draw.select('li.pastWinNumber')]

        # Extract bonus
        bonus_tag = draw.select_one('li.pastWinNumberBonus')
        bonus = bonus_tag.get_text(strip=True).replace("Bonus", "").strip() if bonus_tag else None

        # Extract extra
        extra_tag = draw.select_one('div.pastWinNumExtra')
        extra_number = extra_tag.get_text(strip=True) if extra_tag else None

        # Extract prize breakdown rel URL
        prize_breakdown = draw.select_one('div.pastWinNumPrizeBreakdown')
        draw_number = None
        prize_break_down = None
        if prize_breakdown and 'rel' in prize_breakdown.attrs:
            rel = prize_breakdown['rel']
            prize_break_down = rel
            if "drawNumber=" in rel:
                draw_number = rel.split('drawNumber=')[-1]

        # Extract MAXMILLIONS
        maxmillions_draws = []
        for ul in draw.select('div.pastWinNumMMGroup ul.pastWinNumbers'):
            mm_numbers = [li.get_text(strip=True) for li in ul.select('li.pastWinNumMM')]
            if mm_numbers:
                maxmillions_draws.append(mm_numbers)

        # Prize details and jackpot
        prize_details_data, jackpot_value = get_prize_details_info_649(SOURCE_DATA + prize_break_down)

        # GOLD BALL info extraction
        # gold_ball_info = {}
        # ball_draw_tag = draw.select_one('div.pastWinNumLogoGPD')
        # if ball_draw_tag:
        #     before_strp = ball_draw_tag.get_text(strip=True).split(" ")[-1].lower()
        #     gold_ball_info['ball_drawn'] = before_strp.split(":")[-1]

        # gold_ball_table = draw.select('table.prizeBreakdownTable')
        # winners_list = []

        # if gold_ball_table:
        #     last_table = gold_ball_table[-1]
        #     rows = last_table.find_all('tr')[1:]
        #     for row in rows:
        #         cols = row.find_all('td')
        #         if len(cols) == 3:
        #             # Extract winning number and prize
        #             winning_number = cols[0].get_text(strip=True)
        #             prize = cols[2].get_text(strip=True).replace('$', '').replace(',', '')  # Clean up the prize format

        #             winners_list.append({
        #                 'winning_number': winning_number,
        #                 'prize': prize
        #             })

        # if winners_list:
        #     gold_ball_info['winners'] = winners_list

        # Extract Super Draw info and move it inside the ball_drawn
        # super_draw_info = []

        # super_draw_tag = draw.select_one('div.pastWinNumSuperDraw')
        # if super_draw_tag:
        #     super_draw_data = super_draw_tag.get_text(strip=True)
        #     super_draw_info.append(super_draw_data)

        # if super_draw_info:
        #     gold_ball_info['super_draws'] = super_draw_info

        # Append all data
        draw_data.append({
            'date': formatted_date,
            'draw_number': draw_number,
            'name': game_type,
            'numbers': numbers,
            'jackpot_value': jackpot_value,
            'bonus': bonus,
            'extra': extra_number,
            'maxmillions': maxmillions_draws,
            'prize_break_down': prize_break_down,
            'prize_details_data': prize_details_data,

        })

    # Example of how the data might look in the end
    # print(draw_data)
    return draw_data
