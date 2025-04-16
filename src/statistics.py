import main

# other_file.py
def parse_lotto_max_frequencies(html_content):
    soup = main.BeautifulSoup(html_content, 'html.parser')

    # Initialize dictionaries for main number and bonus ball frequencies
    main_number_freq = {"frequencies": []}
    bonus_ball_freq = {"frequencies": []}

    # Select all the divs that contain a h3 child
    gen_boxes = soup.select('.genBox')
    
    # Loop through each genBox div
    for gen_box in gen_boxes:
        # Find the h3 element inside the genBox div
        h3_tag = gen_box.find('h3')
        
        # Check if the h3 text matches "Main Number Frequencies" or "Bonus Ball Frequencies"
        if h3_tag:
            if h3_tag.get_text(strip=True) == "Main Number Frequencies":
                # Now select the .freqBalls .inner divs inside the relevant genBox
                freq_balls = gen_box.select('.freqBalls .inner')
                
                for ball in freq_balls:
                    number = ball.select_one('.resultBall').get_text(strip=True)  # The number itself
                    frequency = ball.select_one('.text').get_text(strip=True)  # The frequency, like "87 times"
                    
                    # Extract just the number part from the frequency string (e.g., "87 times" -> 87)
                    times = frequency.split()[0]  # The first part is the number

                    main_number_freq['frequencies'].append({
                        'number': number,
                        'frequency': times
                    })
            
            elif h3_tag.get_text(strip=True) == "Bonus Ball Frequencies":
                # Now select the .freqBalls .inner divs inside the relevant genBox
                freq_balls = gen_box.select('.freqBalls .inner')
                
                for ball in freq_balls:
                    number = ball.select_one('.resultBall').get_text(strip=True)  # The number itself
                    frequency = ball.select_one('.text').get_text(strip=True)  # The frequency, like "87 times"
                    
                    # Extract just the number part from the frequency string (e.g., "87 times" -> 87)
                    times = frequency.split()[0]  # The first part is the number

                    bonus_ball_freq['frequencies'].append({
                        'number': number,
                        'frequency': times
                    })

    # Return the separate main_number_freq and bonus_ball_freq in a structured response
    return {
        'main_number_freq': main_number_freq,
        'bonus_ball_freq': bonus_ball_freq
    }
