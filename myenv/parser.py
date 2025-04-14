import models  # Ensure models.py is available and contains save_frequencies()
from datetime import datetime

def parse_lotto_max_frequencies(json_data):
    # Extract frequency lists from the JSON data
    main_number_freq = json_data['main_number_freq']['frequencies']
    bonus_ball_freq = json_data['bonus_ball_freq']['frequencies']

    # Optionally: convert string numbers to integers
    main_number_freq = [
        {"number": int(item["number"]), "frequency": int(item["frequency"])}
        for item in main_number_freq
    ]
    bonus_ball_freq = [
        {"number": int(item["number"]), "frequency": int(item["frequency"])}
        for item in bonus_ball_freq
    ]

    # Prepare result for saving
    result = {
        'main_number_freq': main_number_freq,
        'bonus_ball_freq': bonus_ball_freq
    }

    # Save to DB via models
    models.save_frequencies(result)

    return result


def parse_draw_result(raw_data):
    """
    Parses a list of draw result dictionaries.
    Returns a list of parsed draw dictionaries.
    """

    parsed_draws = []

    for result in raw_data:  # removed .get("results", [])
        draw_date = datetime.strptime(result["date"], "%A, %B %d, %Y").date()

        parsed = {
            "date": draw_date.isoformat(),  # "YYYY-MM-DD"
            "name": result.get("name"),
            "bonus": result.get("bonus"),
            "extra": result.get("extra"),
            "jackpot_value": int(result.get("jackpot_value") or 0),
            "numbers": result.get("numbers", []),
            "past_winning_numbers": result.get("past_winning_numbers", ""),
            "prize_details": result.get("prize_details", []),
        }

        parsed_draws.append(parsed)

    return parsed_draws

