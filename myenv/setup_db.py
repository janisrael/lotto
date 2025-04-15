# setup_db.py
from db import get_connection

def setup():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # draw_results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draw_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_date DATE,
            name VARCHAR(255),
            bonus VARCHAR(20),
            extra VARCHAR(20),
            jackpot_value BIGINT,
            game_id VARCHAR(20),
            draw_number BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # draw_numbers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draw_numbers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_id INT,
            number VARCHAR(5),
            FOREIGN KEY (draw_id) REFERENCES draw_results(id) ON DELETE CASCADE
        )
    ''')

    # prize_details_data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prize_details_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_id INT,
            winners VARCHAR(100),
            prize VARCHAR(50),
            category VARCHAR(50),
            game_id VARCHAR(20)
        )
    """)

    # max_million_results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS max_million_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_id INT,
            numbers VARCHAR(100)
        )
    """)

    # extra_prize_ml
    # cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS extra_prize_ml (
    #         id INT AUTO_INCREMENT PRIMARY KEY,
    #         max_mil_id INT,
    #         winners VARCHAR(50),
    #         prize VARCHAR(50),
    #         category VARCHAR(50)
    #     )
    # """)

    # gold_ball_data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_ball_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_id INT,
            winning_num VARCHAR(50),
            prize VARCHAR(50),
            ball_drawn VARCHAR(20),
            winners VARCHAR(20)
        )
    """)

    # super_draws
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS super_draws (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_id INT,
            numbers INT,
            prize VARCHAR(50),
            winners VARCHAR(50)
        )
    """)

    # extra_prize_details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extra_prize_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_id INT,
            winners VARCHAR(30),
            prize VARCHAR(50),
            category VARCHAR(50),
            game_id VARCHAR(10)
        )
    """)




    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS draw_results (
    #         id INT AUTO_INCREMENT PRIMARY KEY,
    #         draw_date DATE,
    #         name VARCHAR(255),
    #         bonus VARCHAR(5),
    #         extra VARCHAR(20),
    #         jackpot_value BIGINT,
    #         past_winning_numbers TEXT,
    #         prize_details TEXT
    #     )
    # ''')

    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS draw_numbers (
    #         id INT AUTO_INCREMENT PRIMARY KEY,
    #         draw_id INT,
    #         number VARCHAR(5),
    #         FOREIGN KEY (draw_id) REFERENCES draw_results(id) ON DELETE CASCADE
    #     )
    # ''')

    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS prize_details_data (
    #         id INT AUTO_INCREMENT PRIMARY KEY,
    #         draw_id INT,
    #         category VARCHAR(200),
    #         prize VARCHAR(200),
    #         winners VARCHAR(200),
    #         FOREIGN KEY (draw_id) REFERENCES draw_results(id) ON DELETE CASCADE
    #     )
    # ''')

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database Created!")

if __name__ == "__main__":
    setup()