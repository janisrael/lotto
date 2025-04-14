from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to fetch HTML page
def get_page_contents(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None

def extract_prize_table_data(soup):
    prize_tables = soup.select('table.prizeBreakdownTable')
    prize_data = []

    for table in prize_tables:
        rows = table.find_all('tr')[1:]  # Skip header row
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

def get_prize_details_info(url):
    html = get_page_contents(url)
    if not html:
        return {'error': 'Failed to fetch prize details'}
    soup = BeautifulSoup(html, 'html.parser')
    return extract_prize_table_data(soup)

# Function to parse lottery numbers
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
        game_info['date'] = date.get_text(strip=True) if date else 'Unknown'

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

        # ✅ Get all <li class="homePrizeDetails"> and extract their rel values
        prize_details = tab.select('li.homePrizeDetails')
        game_info['prize_details'] = []
        for li in prize_details:
            rel_value = li.get('rel', None)
            if rel_value:
                game_info['prize_details'].append('https://www.wclc.com' + rel_value)

        # Scrape prize details from prize_details URLs
        game_info['prize_details_data'] = []
        for prize_url in game_info['prize_details']:
            prize_data = get_prize_details_info(prize_url)
            game_info['prize_details_data'].append(prize_data)

        results.append(game_info)

    return results

@app.route('/lottery')
def lottery_route():
    url = 'https://www.wclc.com/home.htm'  # You can change this to the actual lotto page
    page_contents = get_page_contents(url)

    if not page_contents:
        return '❌ Failed to retrieve lottery page.'

    lotto_results = parse_lottery_html(page_contents)

    # Return as JSON
    return jsonify({'results': lotto_results})

# Original quote scraping route
def get_quotes_and_authors(page_contents):
    soup = BeautifulSoup(page_contents, 'html.parser')
    quotes = soup.find_all('span', class_='text')
    authors = soup.find_all('small', class_='author')
    return quotes, authors

@app.route('/test')
def test_route():
    url = 'https://www.wclc.com/home.htm'
    page_contents = get_page_contents(url)

    if page_contents:
        quotes, authors = get_quotes_and_authors(page_contents)
        result = '<h1>Quotes:</h1><ul>'
        for i in range(len(quotes)):
            quote = quotes[i].text
            author = authors[i].text
            result += f'<li><strong>{quote}</strong> — {author}</li>'
        result += '</ul>'
        return result
    else:
        return '❌ Failed to retrieve this quotes page.'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
