from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define the lottery result model
class LotteryResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date = db.Column(db.String(100))
    numbers = db.Column(db.String(100))  # List of numbers stored as a comma-separated string
    bonus = db.Column(db.String(10))
    extra = db.Column(db.String(20))
    jackpot = db.Column(db.String(50))

    def __init__(self, name, date, numbers, bonus=None, extra=None, jackpot=None):
        self.name = name
        self.date = date
        self.numbers = numbers
        self.bonus = bonus
        self.extra = extra
        self.jackpot = jackpot
