import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "lotterydb"
}

# Context manager to handle connections
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def create_tables():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS main_number_frequencies (
                number VARCHAR(5) PRIMARY KEY,
                frequency INT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bonus_ball_frequencies (
                number VARCHAR(5) PRIMARY KEY,
                frequency INT
            )
        ''')
        conn.commit()

def save_frequencies(freq_data):
    with get_connection() as conn:
        cursor = conn.cursor()
        for item in freq_data['main_number_freq']:
            cursor.execute('''
                INSERT INTO main_number_frequencies (number, frequency)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE frequency = VALUES(frequency)
            ''', (item['number'], int(item['frequency'])))

        for item in freq_data['bonus_ball_freq']:
            cursor.execute('''
                INSERT INTO bonus_ball_frequencies (number, frequency)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE frequency = VALUES(frequency)
            ''', (item['number'], int(item['frequency'])))
        
        conn.commit()

def get_latest_frequencies():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT number, frequency FROM main_number_frequencies")
        main_data = [{"number": int(row[0]), "frequency": int(row[1])} for row in cursor.fetchall()]

        cursor.execute("SELECT number, frequency FROM bonus_ball_frequencies")
        bonus_data = [{"number": int(row[0]), "frequency": int(row[1])} for row in cursor.fetchall()]

        if not main_data and not bonus_data:
            return None

        return {
            "main_number_freq": main_data,
            "bonus_ball_freq": bonus_data
        }



def create_draw_tables():
     with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS draw_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                draw_date DATE UNIQUE,
                name VARCHAR(255),
                bonus VARCHAR(5),
                extra VARCHAR(20),
                jackpot_value BIGINT,
                past_winning_numbers TEXT,
                prize_details TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS draw_numbers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                draw_id INT,
                number VARCHAR(5),
                FOREIGN KEY (draw_id) REFERENCES draw_results(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prize_details_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                draw_id INT,
                category VARCHAR(200),
                prize VARCHAR(200),
                winners VARCHAR(200),
                FOREIGN KEY (draw_id) REFERENCES draw_results(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()

# --- DATA INSERTION ---
def save_draw_result(draw):
    if not isinstance(draw, dict):
        raise ValueError("Expected a single draw dictionary")

    with get_connection() as conn:
        cursor = conn.cursor()

        # Check if the draw date already exists
        cursor.execute("SELECT COUNT(1) FROM draw_results WHERE draw_date = %s", (draw["date"],))
        if cursor.fetchone()[0] > 0:
            print(f"Draw date {draw['date']} already exists. Skipping save.")
            return  # Skip saving if the date already exists

        # Insert the draw result
        cursor.execute("""
            INSERT INTO draw_results (
                draw_date, name, bonus, extra, jackpot_value,
                past_winning_numbers, prize_details
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            draw["date"],
            draw["name"],
            draw["bonus"],
            draw["extra"],
            int(draw.get("jackpot_value", 0)),
            draw.get("past_winning_numbers", ""),
            ",".join(draw.get("prize_details", []))
        ))

        conn.commit()

        # Retrieve the inserted draw ID
        cursor.execute("SELECT id FROM draw_results WHERE draw_date = %s", (draw["date"],))
        draw_id = cursor.fetchone()[0]
        
        # Insert the draw numbers
        for number in draw["numbers"]:
            cursor.execute("""
                INSERT INTO draw_numbers (draw_id, number)
                VALUES (%s, %s)
            """, (draw_id, number))

            # Insert the draw numbers
        for prize_group in draw.get("prize_details_data", []):
            for prize in prize_group:
                cursor.execute("""
                    INSERT INTO prize_details_data (draw_id, category, prize, winners)
                    VALUES (%s, %s, %s, %s)
                """, (
                    draw_id,
                    prize.get("category"),
                    prize.get("prize"),
                    prize.get("winners")
                ))

        conn.commit()



# --- DATA RETRIEVAL ---

def get_latest_draw():
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        # Get latest result
        cursor.execute("""
            SELECT * FROM draw_results ORDER BY draw_date DESC LIMIT 1
        """)
        draw = cursor.fetchone()

        if not draw:
            return None

        # Get associated numbers
        cursor.execute("SELECT number FROM draw_numbers WHERE draw_id = %s", (draw["id"],))
        numbers = [row["number"] for row in cursor.fetchall()]
        draw["numbers"] = numbers
       
        return draw
