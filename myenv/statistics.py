import main

# other_file.py
def parse_lotto_max_frequencies(html_content):
    soup = main.BeautifulSoup(html_content, 'html.parser')
    results = []

    # Select all the divs that contain the ball number and frequency
    freq_balls = soup.select('.genBox .freqBalls .inner')
    
    for ball in freq_balls:
        number = ball.select_one('.resultBall').get_text(strip=True)  # The number itself
        frequency = ball.select_one('.text').get_text(strip=True)  # The frequency, like "87 times"

        # Extract just the number part from the frequency string (e.g., "87 times" -> 87)
        times = frequency.split()[0]  # The first part is the number

        results.append({
            'number': number,
            'frequency': times
        })

    return results