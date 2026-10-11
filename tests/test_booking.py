import datetime
from main import app
from models import db, TrainingSession

TOMORROW = datetime.date.today() + datetime.timedelta(days=1)

def login(client, email):
    return client.post("/login", data={"email":email, "password":"pw"})

def booking_form(ids, start="08:00", duration=60):
    """Dữ liệu y như form /create-sesison gửi lên."""
    return {
        "date": TOMORROW.isoformat(),
        "start_time": start,
        "duration": duration,
        "member_id": ids["member"],
        "package": ids["package"],
        "session_type": "",
        "notes": "",
    }

def count_sessions():
    with app.app_context():
        return len(db.session.execute(db.select(TrainingSession)).scalars().all())

def test_coach_dat_lich_thanh_cong(client, ids):
    login(client, "coach@monkey.com")
    response = client.post("/create-session",data=booking_form(ids))
    assert response.status_code == 302 #thành công -> chuyển sang /schedule
    assert count_sessions() == 1

def test_trung_gio_bi_chan(client,ids):
    login(client, "coach@monkey.com")
    client.post("/create-session", data=booking_form(ids))
    response = client.post("/create-session",data=booking_form(ids))
    assert "Slot is already booked" in response.get_data(as_text=True)
    assert count_sessions() == 1   #buổi thứ 2 KHÔNG được lưu
    