# import mysql.connector
from db import get_connection
from datetime import date

conn = get_connection()

# --- DATA RETRIEVAL ---

def get_latest_draw(game_type):
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        # Check if draw_results table exists
        cursor.execute("""
            SELECT COUNT(*) AS table_exists
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = 'draw_results'
        """)
        result = cursor.fetchone()
        
        if not result or result["table_exists"] == 0:
            return 'No Data'
            # return None  # or raise an exception if you prefer

        if game_type == 'lottoMax':
            cursor.execute("""
                SELECT * FROM draw_results
                WHERE name = %s
                ORDER BY draw_date DESC LIMIT 1
            """, ("LOTTO MAX Winning Numbers",))


        elif game_type == 'lotto649':
            cursor.execute("""
                SELECT * FROM draw_results
                WHERE name = %s
                ORDER BY draw_date DESC LIMIT 1
            """, ("LOTTO 6/49 Winning Numbers",))

        elif game_type == 'dailyGrand':
            cursor.execute("""
                SELECT * FROM draw_results
                WHERE name = %s
                ORDER BY draw_date DESC LIMIT 1
            """, ("DAILY GRAND Winning Numbers",))

        # Get latest result
        elif game_type == 'all':
            cursor.execute("""
                SELECT dr.*
                FROM draw_results dr
                JOIN (
                    SELECT name, MAX(draw_date) AS latest_date
                    FROM draw_results
                    GROUP BY name
                ) latest
                ON dr.name = latest.name AND dr.draw_date = latest.latest_date
                ORDER BY dr.draw_date DESC
            """)
            

        else:
            cursor.execute("""
                SELECT * FROM draw_results ORDER BY id ASC
            """)
        
        draw = cursor.fetchall()

        if not draw:
            return None

        # Get associated numbers
        for pr in draw:
            cursor.execute("SELECT * FROM prize_details_data WHERE draw_id = %s", (pr["id"],))
            prizes = cursor.fetchall()
            # dra['prize_details_data'] = prizes
            if prizes:
                pr["prize_details_data"] = prizes
            else:
                pr["prize_details_data"] = ''

        for pr in draw:
            # 1) Initialize the structure once
            pr["prize_details_data"] = {
                "extra_price_breakdown": [],
                "gold_ball_drawn": {},
                "prize_data": [],
                "super_draws": []
            }

            # 2) prize_data
            cursor.execute(
                "SELECT * FROM prize_details_data WHERE draw_id = %s",
                (pr["id"],)
            )
            prizes = cursor.fetchall()
            if prizes:
                pr["prize_details_data"]["prize_data"] = prizes

            # 3) gold_ball and super_draws only for 6-49 games
            if pr["game_id"] in ('6-49', 'W6-49'):
                # 3a) gold_ball_drawn
                cursor.execute(
                    "SELECT * FROM gold_ball_data WHERE draw_id = %s",
                    (pr["id"],)
                )
                balls = cursor.fetchall()
                if balls:
                    # if you only ever expect one row, you can do balls[0]
                    pr["prize_details_data"]["gold_ball_drawn"] = balls[0]

                # 3b) super_draws
                cursor.execute(
                    "SELECT * FROM super_draws WHERE draw_id = %s",
                    (pr["id"],)
                )
                super_draws = cursor.fetchall()
                if super_draws:
                    pr["prize_details_data"]["super_draws"] = super_draws

            # 4) extra_price_breakdown
            cursor.execute(
                "SELECT * FROM extra_prize_details WHERE draw_id = %s",
                (pr["id"],)
            )
            extra = cursor.fetchall()
            if extra:
                pr["prize_details_data"]["extra_price_breakdown"] = extra


        for dr in draw:
            cursor.execute("SELECT number FROM draw_numbers WHERE draw_id = %s", (dr["id"],))
            numbers = [row["number"] for row in cursor.fetchall()]
            if numbers:
                dr["numbers"] = numbers
            else:
                dr["numbers"] = ''

       
        cursor.execute("""
            SELECT jp.game, jp.prize, jp.created_at
            FROM jackpot_prize jp
            INNER JOIN (
                SELECT 
                    game, 
                    MAX(created_at) AS latest_created_at
                FROM jackpot_prize
                GROUP BY game
            ) latest
            ON jp.game = latest.game
            AND jp.created_at = latest.latest_created_at
        """)
        latest_jackpots = cursor.fetchall()
        
        data = {
            "results": draw,
            "jackpot": latest_jackpots
        }
        return data
    

def get_past_draw(game_id, start_date=None, end_date=None):

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        # Check if draw_results table exists
        cursor.execute("""
            SELECT COUNT(*) AS table_exists
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = 'draw_results'
        """)
        result = cursor.fetchone()
        
        if not result or result["table_exists"] == 0:
            return 'No Data'
            # return None  # or raise an exception if you prefer
        print(game_id)
         
        query = """
            SELECT * FROM draw_results
            WHERE game_id = %s
        """
        params = [game_id]

        if start_date:
            query += " AND draw_date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND draw_date <= %s"
            params.append(end_date)

        query += " ORDER BY draw_date DESC"

        # 👇 Applying it in cursor.execute
        cursor.execute(query, tuple(params))

        draw = cursor.fetchall()

        if not draw:
            return None

        # Get associated numbers
        for pr in draw:
            cursor.execute("SELECT * FROM prize_details_data WHERE draw_id = %s", (pr["id"],))
            prizes = cursor.fetchall()
            # dra['prize_details_data'] = prizes
            if prizes:
                pr["prize_details_data"] = prizes
            else:
                pr["prize_details_data"] = ''

        for pr in draw:
            # 1) Initialize the structure once
            pr["prize_details_data"] = {
                "extra_price_breakdown": [],
                "gold_ball_drawn": {},
                "prize_data": [],
                "super_draws": []
            }

            # 2) prize_data
            cursor.execute(
                "SELECT * FROM prize_details_data WHERE draw_id = %s",
                (pr["id"],)
            )
            prizes = cursor.fetchall()
            if prizes:
                pr["prize_details_data"]["prize_data"] = prizes

            # 3) gold_ball and super_draws only for 6-49 games
            if pr["game_id"] in ('6-49', 'W6-49'):
                # 3a) gold_ball_drawn
                cursor.execute(
                    "SELECT * FROM gold_ball_data WHERE draw_id = %s",
                    (pr["id"],)
                )
                balls = cursor.fetchall()
                if balls:
                    # if you only ever expect one row, you can do balls[0]
                    pr["prize_details_data"]["gold_ball_drawn"] = balls[0]

                # 3b) super_draws
                cursor.execute(
                    "SELECT * FROM super_draws WHERE draw_id = %s",
                    (pr["id"],)
                )
                super_draws = cursor.fetchall()
                if super_draws:
                    pr["prize_details_data"]["super_draws"] = super_draws

            # 4) extra_price_breakdown
            cursor.execute(
                "SELECT * FROM extra_prize_details WHERE draw_id = %s",
                (pr["id"],)
            )
            extra = cursor.fetchall()
            if extra:
                pr["prize_details_data"]["extra_price_breakdown"] = extra


        for dr in draw:
            cursor.execute("SELECT number FROM draw_numbers WHERE draw_id = %s", (dr["id"],))
            numbers = [row["number"] for row in cursor.fetchall()]
            if numbers:
                dr["numbers"] = numbers
            else:
                dr["numbers"] = ''

       
        # cursor.execute("""
        #     SELECT jp.game, jp.prize, jp.created_at
        #     FROM jackpot_prize jp
        #     INNER JOIN (
        #         SELECT 
        #             game, 
        #             MAX(created_at) AS latest_created_at
        #         FROM jackpot_prize
        #         GROUP BY game
        #     ) latest
        #     ON jp.game = latest.game
        #     AND jp.created_at = latest.latest_created_at
        # """)
        # latest_jackpots = cursor.fetchall()
        
        # data = {
        #     "results": draw,
        #     "jackpot": latest_jackpots
        # }
        return draw