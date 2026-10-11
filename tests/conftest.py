import os

os.environ["DATABASE_URL"] ="sqlite://"
os.environ["LOGIN_KEY"] = "test-key"

import pytest
from werkzeug.security import generate_password_hash
from main import app
from models import db, User, Package

@pytest.fixture
def ids():
    """Tạo database trống 3 users + 1 gói tập. Trả về id của từng thứ."""
    app.config["WTF_CSRF_ENABLED"] = False #Tắt CSRF khi test
    with app.app_context():
        db.drop_all() #Xóa sạch -> mỗi test bắt đầu từ 0
        db.create_all()

        pw = generate_password_hash("pw")
        admin = User(name="Admin", email="admin@monkey.com", password_hash=pw, role="admin", phone="1")
        coach = User(name="Coach", email="coach@monkey.com", password_hash=pw, role="coach", phone="1")
        member = User(name="Member", email="member@monkey.com",password_hash=pw, role="member", phone="1")
        db.session.add_all([admin,coach,member])
        db.session.commit()

        pack = Package(package_name="Warrior", number_of_session=10, member_id = member.id, coach_id=coach.id)
        db.session.add(pack)
        db.session.commit()

        return {"admin": admin.id, "coach": coach.id, "member": member.id, "package": pack.id}

@pytest.fixture
def client(ids):
    """Trình duyệt giả. Phụ thuộc ids -> database luôn được tạo trước."""
    return app.test_client()

