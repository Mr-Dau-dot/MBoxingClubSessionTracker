import datetime
from sqlalchemy.exc import IntegrityError
from functools import wraps
from flask import Flask, request, render_template, abort, url_for, flash, session
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, Boolean, DateTime, Time
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from dotenv import load_dotenv
from werkzeug.utils import redirect

from forms import LoginForm, RegisterForm, SessionForm
import os
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SECRET_KEY"] = os.environ.get("LOGIN_KEY")

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(UserMixin,db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String,nullable=False)
    email: Mapped[str] = mapped_column(String,unique=True,nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    join_date: Mapped[datetime] = mapped_column(DateTime,default=datetime.datetime.today, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean,default=True, nullable=False)
    session_as_coach = relationship("TrainingSession", foreign_keys="TrainingSession.coach_id",
                                    back_populates="coach")
    session_as_member = relationship("TrainingSession", foreign_keys="TrainingSession.member_id",
                                     back_populates="member")


class TrainingSession(db.Model):
    __tablename__ = "training_session"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime,default=datetime.datetime.today,nullable=False)
    start_time: Mapped[datetime] = mapped_column(Time,nullable=False)
    end_time: Mapped[datetime] = mapped_column(Time,nullable=False)
    session_type: Mapped[str] = mapped_column(String,nullable=True)
    notes: Mapped[str] = mapped_column(String,nullable=True)
    coach_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=False)
    member_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=False)

    coach = relationship("User", foreign_keys=[coach_id], back_populates="session_as_coach")
    member = relationship("User", foreign_keys=[member_id], back_populates="session_as_member")
# with app.app_context():
#     db.create_all()
#     coach = User(
#         name="Nghia Anh",
#         email="haha@gmail.com",
#         password_hash = "test",
#         role="coach",
#         status=True,
#         join_date = datetime.datetime.today()
#     )
#     member = User (
#         name="HuongTran",
#         email="huong@gmail.com",
#         password_hash = "test",
#         join_date=datetime.datetime.today(),
#         role="member",
#         status=True
#     )
#     db.session.add_all([coach, member])
#     db.session.commit()
#
#     session = TrainingSession(
#         start_time= datetime.datetime.now(),
#         end_time = datetime.datetime.now() + datetime.timedelta(hours=1),
#         coach_id = coach.id,
#         member_id = member.id
#     )
#
#     db.session.add(session)
#     db.session.commit()

    # print("Coach's session:", session.coach.name)
    # print("Coach teaching session", session.member.name)
    # print("Nghia Anh's Session:", coach.session_as_coach)

def roles_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args,**kwargs):
            if current_user.role not in allowed_roles:
                return abort(403)
            return view_func(*args,**kwargs)
        return wrapped_view
    return decorator



@app.route("/")
def home():
    return f"Welcome to Monkey Boxing Club"

@app.route("/register",methods=["GET","POST"])
def sign_up():
    form = RegisterForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()

        if user:
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email= form.email.data,
            name=form.name.data,
            password_hash=hash_and_salted_password,
            phone=form.phone.data,
            role="member"

        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("dash_board"))
    return render_template('register.html',form=form, current_user=current_user)


    # if form.validate_on_submit():
    #     name = request.form.get('name')
    #     email = request.form.get('email')
    #     password = request.form.get('password')
    #     phone = request.form.get('phone')
    #
    #     password_hash = generate_password_hash(
    #         password,
    #         method= 'pbkdf2:sha256',
    #         salt_length = 8
    #     )
    #     try:
    #         new_user = User(
    #             name=name,
    #             email=email,
    #             password_hash=password_hash,
    #             role="member",
    #             phone=phone
    #         )
    #         db.session.add(new_user)
    #         db.session.commit()
    #     except IntegrityError:
    #         db.session.rollback()
    #         return f"This email is already existed, please try another email!"
    #
    #     return f"Successfully signed up!"

@app.route("/login", methods=["GET","POST"])

def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()

        if not user:
            flash("Password or Email is incorrect, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password_hash, password):
            flash('Password or email is incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('dash_board'))
    return render_template("login.html",form=form, current_user=current_user)




    # email = request.form.get('email')
    # password = request.form.get('password')
    # user = User.query.filter_by(email=email).first()
    # if not user:
    #     return f"Your email or password is incorrect"
    # else:
    #     if check_password_hash(user.password_hash,password):
    #         login_user(user)
    #         return user.name
    #     else:
    #         return f"Your email or password is incorrect"


@app.route("/dashboard")
@login_required
@roles_required("coach","admin")
def dash_board():
    return f"Welcome the club {current_user.name}, you are the best {current_user.role} here."


@app.route("/create-session",methods=["GET","POST"])
@login_required
@roles_required("coach","admin")
def create_session():
    form = SessionForm()
    results = db.session.execute(db.select(User).where(User.role == "member"))
    members = results.scalars().all()
    form.member_id.choices = [(m.id, m.name) for m in members]
    if form.validate_on_submit():
        new_session = TrainingSession(
            member_id= form.member_id.data,
            coach_id= current_user.id,
            date= form.date.data,
            start_time= form.start_time.data,
            end_time= form.end_time.data,
            session_type = form.session_type.data,
            notes= form.notes.data,
        )

        db.session.add(new_session)
        db.session.commit()
        return redirect(url_for("dash_board"))
    return render_template("new_session.html",form=form)

@app.route('/sessions')
@login_required
def show_sessions():
    if current_user.role == "member":
        query = db.select(TrainingSession).where(TrainingSession.member_id == current_user.id)
    elif current_user.role == "coach":
        query = db.select(TrainingSession).where(TrainingSession.coach_id == current_user.id)
    else:
        query = db.select(TrainingSession)

    sessions = db.session.execute(query.order_by(TrainingSession.date)).scalars().all()
    return render_template("sessions.html", sessions=sessions)

@app.route("/delete-session/<int:session_id>")
@login_required
@roles_required("coach","admin")
def delete_session(session_id):
    session_to_delete = db.session.get(TrainingSession, session_id)
    if session_to_delete.coach_id == current_user.id or current_user.role == "admin": #admin.id = 1:
        db.session.delete(session_to_delete)
        db.session.commit()
    return redirect(url_for("show_sessions"))

@app.route("/update-session/<int:session_id>",methods=["GET","POST"])
@login_required
@roles_required("coach","admin")
def update_session(session_id):
    session_to_update = db.get_or_404(TrainingSession, session_id)
    if session_to_update.coach_id == current_user.id or current_user.role == "admin":
        edit_form = SessionForm(
            member_id= session_to_update.member_id,
            coach_id=current_user.id,
            date= session_to_update.date,
            start_time=session_to_update.start_time,
            end_time=session_to_update.end_time,
            session_type=session_to_update.session_type,
            notes=session_to_update.notes,
        )

        members = db.session.execute(db.select(User).where(User.role == "member")).scalars().all()
        edit_form.member_id.choices = [(m.id, m.name) for m in members]
        if edit_form.validate_on_submit():
            session_to_update.member_id = edit_form.member_id.data
            session_to_update.start_time = edit_form.start_time.data
            session_to_update.end_time = edit_form.end_time.data
            session_to_update.date = edit_form.date.data
            session_to_update.session_type = edit_form.session_type.data
            session_to_update.notes = edit_form.notes.data
            db.session.commit()
            return redirect(url_for('show_sessions'))
        return render_template("new_session.html",form=edit_form)

    else:
        return abort(403)
if __name__ == "__main__":
    app.run(debug=True)