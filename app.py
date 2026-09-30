from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


class Reminder(db.Model):
    __tablename__ = 'reminders'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Text, nullable=False)
    remind_at = db.Column(db.DateTime(timezone=True), nullable=False)
    is_notified = db.Column(db.Boolean, default=False)


    def to_dict(self):
        return {
            "id": self.id,
            "task": self.task,
            "remind_at": self.remind_at.isoformat(),
            "is_notified": self.is_notified
        }


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/reminders', methods=['GET', 'POST'])
def handle_reminders():
    if request.method == 'POST':
        data = request.get_json()
        new_item = Reminder(
            task=data['task'],
            remind_at=datetime.fromisoformat(data['remind_at'])
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.to_dict()), 201


    reminders = Reminder.query.order_by(Reminder.remind_at.asc()).all()
    return jsonify([r.to_dict() for r in reminders])


@app.route('/api/check-reminders', methods=['GET'])
def check_reminders():
    now = datetime.now(timezone.utc)
    due = Reminder.query.filter(Reminder.remind_at <= now, Reminder.is_notified == False).all()
   
    result = [r.to_dict() for r in due]
    for r in due:
        r.is_notified = True
    db.session.commit()
   
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
