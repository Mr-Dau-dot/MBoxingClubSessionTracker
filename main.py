import datetime
from email.policy import default
import click
from datetime import timedelta
from sqlalchemy.exc import IntegrityError
from functools import wraps
from flask import Flask, request, render_template, abort, url_for, flash, session, jsonify
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, Boolean, DateTime, Time, Date
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, foreign
from dotenv import load_dotenv
from sqlalchemy.orm.attributes import backref_listeners
from werkzeug.utils import redirect
from helpers import parse_session_time, duration_minutes_calculated, package_lookup
from forms import LoginForm, RegisterForm, SessionForm, PackageForm
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
    member_package = relationship("Package",foreign_keys="Package.member_id",back_populates="member")
    coach_package = relationship("Package", foreign_keys="Package.coach_id",back_populates="coach")

class TrainingSession(db.Model):
    __tablename__ = "training_session"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date,default=datetime.date.today,nullable=False)
    start_time: Mapped[datetime] = mapped_column(Time,nullable=False)
    end_time: Mapped[datetime] = mapped_column(Time,nullable=False)
    session_type: Mapped[str] = mapped_column(String,nullable=True)
    session_status: Mapped[str] = mapped_column(String,default="scheduled",nullable=False)
    notes: Mapped[str] = mapped_column(String,nullable=True)

    coach_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=False)
    member_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=False)
    coach = relationship("User", foreign_keys=[coach_id], back_populates="session_as_coach")
    member = relationship("User", foreign_keys=[member_id], back_populates="session_as_member")

    package_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("package.id"), nullable=False)
    package = relationship("Package",back_populates="sessions")

class Package(db.Model):
    __tablename__ = "package"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    package_name: Mapped[str] = mapped_column(String,nullable=False)
    package_starting_date: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today,nullable=False)
    number_of_session: Mapped[int] = mapped_column(Integer,nullable=False)
    member_id: Mapped[int] = mapped_column(Integer,db.ForeignKey("users.id"),nullable=False)
    coach_id: Mapped[int] = mapped_column(Integer,db.ForeignKey("users.id"),nullable=False)
    member = relationship("User",foreign_keys=[member_id],back_populates="member_package")
    coach = relationship("User",foreign_keys=[coach_id],back_populates="coach_package")
    sessions = relationship("TrainingSession",back_populates="package")

with app.app_context():
    db.create_all()


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


@app.route("/dashboard")
@login_required
@roles_required("coach","admin")
def dash_board():
    return f"Welcome the club {current_user.name}, you are the best {current_user.role} here."

#DETECTING CONFLICTS SCHEDULE
def has_conflict(new_start, new_end, existing_sessions):
    for detecting_session in existing_sessions:
        if (new_end <= detecting_session.start_time) or (new_start >= detecting_session.end_time):
            continue
        else:
            return True
    return False

@app.route("/create-package",methods=["GET","POST"])
@login_required
@roles_required("coach","admin")
def create_package():
    form = PackageForm()
    member_results = db.session.execute(db.select(User).where(User.role == "member"))
    coach_results = db.session.execute(db.select(User).where(User.role == "coach"))
    members = member_results.scalars().all()
    form.member_id.choices = [(0, "-- Member --")] + [(m.id, m.name) for m in members]
    coach = coach_results.scalars().all()
    form.coach_id.choices = [(0, "-- Coach --")] + [(c.id, c.name) for c in coach]
    if form.validate_on_submit():
        package = package_lookup(form.name.data)
        if current_user.role == "coach":
            new_package = Package(
                package_name = package[0],
                package_starting_date = form.date.data,
                number_of_session = package[1],
                member_id = form.member_id.data,
                coach_id = current_user.id
            )
        else:
            coach_id = form.coach_id.data
            if not coach_id:
                flash("Please choose member's coach")
                return render_template("new_package.html",form=form)
            else:
                new_package = Package(
                    package_name=package[0],
                    package_starting_date=form.date.data,
                    number_of_session=package[1],
                    member_id=form.member_id.data,
                    coach_id=coach_id
                )
        db.session.add(new_package)
        db.session.commit()
        return redirect(url_for("dash_board"))
    return render_template("new_package.html",form=form)


#TARGETING PACKAGE FOR MEMBER-COACH
@app.route("/package-for/<int:member_id>")
@login_required
@roles_required("coach","admin")
def package_for_pair(member_id):

    if current_user.role == "coach":
        coach_id = current_user.id
    else:
        coach_id = request.args.get("coach_id",type=int)

    get_data = db.session.execute(
        db.select(Package).where(Package.coach_id == coach_id, Package.member_id == member_id)
    )
    packages = get_data.scalars().all()
    result = []
    for pack in packages:
        used = len([s for s in pack.sessions if s.session_status != "cancelled"])
        if used < pack.number_of_session:
            result.append({"id": pack.id, "label": f"{pack.package_name} ({pack.number_of_session} sessions)"})
    return jsonify(result)


@app.route("/create-session",methods=["GET","POST"])
@login_required
@roles_required("coach","admin")
def create_session():
    form = SessionForm()
    member_results = db.session.execute(db.select(User).where(User.role == "member"))
    coach_results = db.session.execute(db.select(User).where(User.role == "coach"))

    members = member_results.scalars().all()
    form.member_id.choices = [(0, "-- Member --")] + [(m.id, m.name) for m in members]
    coach = coach_results.scalars().all()
    form.coach_id.choices = [(0, "-- Coach --")] + [ (c.id,c.name) for c in coach]

    if current_user.role == "coach":
        coach_id = current_user.id
    else:
        coach_id = form.coach_id.data

    form.package.choices = db.session.execute(
        db.select(Package).where(Package.coach_id == coach_id, Package.member_id == form.member_id.data)
    ).scalars().all()
    result = []

    for pack in form.package.choices:
        used = len([s for s in pack.sessions if
                    s.session_status != "cancelled"])
        remaining = pack.number_of_session - used
        if used < pack.number_of_session:
            result.append({
                "id": pack.id,
                "label": f"{pack.package_name} ({remaining} remaining)"
            })
    form.package.choices = [tuple(d.values()) for d in result]

    if form.validate_on_submit():
        if current_user.role == "coach":
            time_data = parse_session_time(form.start_time.data,form.duration.data)
            new_session = TrainingSession(
                member_id= form.member_id.data,
                coach_id= current_user.id,
                date= form.date.data,
                start_time= time_data[0],
                end_time= time_data[1],
                session_type = form.session_type.data,
                notes= form.notes.data,
                package_id= form.package.data
            )
        else:
            time_data = parse_session_time(form.start_time.data,form.duration.data)
            if not form.coach_id.data:
                flash("Please choose member's coach")
                return render_template("new_session.html",form=form)
            else:

                new_session = TrainingSession(
                    member_id=form.member_id.data,
                    coach_id=coach_id,
                    date=form.date.data,
                    start_time=time_data[0],
                    end_time=time_data[1],
                    session_type=form.session_type.data,
                    notes=form.notes.data,
                    package_id= form.package.data
                )

        existing_sessions = db.session.execute(
            (db.select(TrainingSession).where(
                TrainingSession.date == new_session.date,
                TrainingSession.coach_id == new_session.coach_id)
            )
        ).scalars().all()
        if has_conflict(time_data[0],
                        time_data[1],
                        existing_sessions):
            flash("Slot is already booked!")
            return render_template("new_session.html",form=form)

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

#MARK ATTENDED/CANCEL SESSION
@app.route("/mark-attended/<int:session_id>",methods=["POST"]) #ATTENDED
@login_required
def mark_attended(session_id):
    session_to_mark = db.get_or_404(TrainingSession, session_id)
    if session_to_mark.coach_id != current_user.id and current_user.role != "admin":
        return abort(403)
    session_to_mark.session_status = "attended"
    db.session.commit()
    return redirect(url_for("schedule"))

@app.route("/cancel-session/<int:session_id>",methods=["POST"]) #CANCELED
@login_required
def cancel_session(session_id):
    session_to_cancel = db.get_or_404(TrainingSession, session_id)
    if session_to_cancel.coach_id != current_user.id and current_user.role != "admin":
        return abort(403)
    session_to_cancel.session_status = "cancelled"
    db.session.commit()
    return redirect(url_for("schedule"))


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
            coach_id=session_to_update.coach_id,
            date= session_to_update.date,
            start_time=session_to_update.start_time.strftime("%H:%M"),
            duration=duration_minutes_calculated(session_to_update.start_time,session_to_update.end_time),
            # end_time=session_to_update.start_time.data + session_to_update.duration.data,
            session_type=session_to_update.session_type,
            notes=session_to_update.notes,
        )

        members = db.session.execute(db.select(User).where(User.role == "member" )).scalars().all()
        edit_form.member_id.choices = [(m.id, m.name) for m in members]
        coach = db.session.execute(db.select(User).where(User.role == "coach" )).scalars().all()
        edit_form.coach_id.choices = [(0, "-- Coach --")] + [(c.id,c.name) for c in coach]

        if edit_form.validate_on_submit():
            time_data = parse_session_time(edit_form.start_time.data,edit_form.duration.data)
            if not edit_form.coach_id.data:
                flash("Please choose member's coach")
                return render_template("new_session.html",form=edit_form)
            else:
                session_to_update.member_id = edit_form.member_id.data
                session_to_update.coach_id = edit_form.coach_id.data
                session_to_update.start_time = time_data[0]
                session_to_update.end_time = time_data[1]
                session_to_update.date = edit_form.date.data
                session_to_update.session_type = edit_form.session_type.data
                session_to_update.notes = edit_form.notes.data
                #session_to_update.package_id = edit_form.package.data

                existing_sessions = db.session.execute(
                    (db.select(TrainingSession).where(
                        TrainingSession.date == session_to_update.date,
                        TrainingSession.coach_id == session_to_update.coach_id,
                        TrainingSession.id != session_to_update.id)
                    )
                ).scalars().all()
                if has_conflict(time_data[0],
                                time_data[1],
                                existing_sessions):
                    flash("Slot is already booked!")
                    return render_template("new_session.html",form=edit_form)

                db.session.commit()
                return redirect(url_for('schedule'))
        return render_template("new_session.html",form=edit_form)

    else:
        return abort(403)


@app.route("/schedule")
@login_required
def schedule():
    today_session = db.session.execute(db.select(TrainingSession).where(TrainingSession.date == datetime.date.today())).scalars().all()
    coach_row = db.session.execute(db.select(User).where(User.role == "coach")).scalars().all()
    table={hour: {coach.id:None for coach in coach_row} for hour in range(7,21)}
    for session in today_session:
        hour_stamp = session.start_time.hour
        if session.end_time.minute == 0:
            end_hour_cutoff = session.end_time.hour
        else:
            end_hour_cutoff = session.end_time.hour + 1
        end_hour_cutoff = min(end_hour_cutoff, 21)
        for h in range(hour_stamp, end_hour_cutoff):
            table[h][session.coach_id] = {"member_id": session.member_id, "member_name": session.member.name}
    print(table)
    return render_template("schedule.html",table=table,coach_row=coach_row)


@app.route("/report")
@login_required
@roles_required("coach","admin")
def report():
    pass


@app.cli.command("create-admin")
def create_admin():
    email = click.prompt("Email")
    password = click.prompt("Password",hide_input=True)
    name = click.prompt("Name")
    phone = click.prompt("Phone")

    admins = db.session.execute(db.select(User).where(User.email == email)).scalar()

    if admins:
        print(f"You've already an admin")
    else:
        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email= email,
            name = name,
            password_hash = hash_and_salted_password,
            phone = phone,
            role = "admin"
        )

        db.session.add(new_user)
        db.session.commit()

        print(f"Successfully create admin account name {name}.")



if __name__ == "__main__":
    app.run(debug=True)