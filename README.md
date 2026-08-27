# MBoxing Club — Training Tracker

A full-stack web app I'm building to track personal training sessions for a boxing club in Hanoi, replacing a paid gym-management SaaS the club was only using for a fraction of its features. Built as part of my ongoing work through Angela Yu's 100 Days of Code bootcamp, extended well past the course curriculum.

## What it does

- Coaches log training sessions (date, time, type, notes) tied to a specific member
- Members log in and see only their own session history
- Coaches see only the sessions they personally teach; admins see everything
- Full CRUD on sessions — create, view, edit, delete
- Summary reporting by day/month/year (in progress)

## Why it exists

The club runs on a 1-on-1 personal training model — one coach, one member, per session, all the way through. The commercial software the club pays for (NextX GymMaster) ships with billing, RFID/fingerprint door access, POS, and multi-branch management — none of which the club actually uses; payments go through bank transfer QR directly, outside any software. After mapping out what the club *actually* uses it for (check-in + attendance history), I concluded a focused internal tool could realistically replace it, so I'm building one.

## Stack

- **Backend:** Flask, Flask-SQLAlchemy (2.0-style `Mapped`/`mapped_column`), Flask-Login, Flask-WTF
- **Database:** PostgreSQL, hosted on Neon (cloud, Singapore region)
- **Auth:** Session-based login, password hashing (`werkzeug.security`), custom role-based access control (`@roles_required` decorator I wrote — a 3-layer decorator factory)
- **Deploy target:** Render (Neon Postgres already provisioned)

## A few design decisions I made along the way

- **Modeled the business, not a generic template.** Considered a many-to-many `Attendance` table (typical for group classes) before realizing the club's actual 1-coach-to-1-member model made a simpler direct foreign-key relationship the correct fit — and cut a table I didn't need.
- **Two layers of authorization.** Role-based (`roles_required("coach","admin")` blocks by account type) and data-level (a coach can only edit/delete *their own* sessions, a member can only see *their own* schedule) — these are separate concerns and both are needed.
- **Didn't trust the client.** Role is hardcoded server-side on registration (`role="member"`), never taken from client-submitted form data, to prevent privilege escalation.
- **Caught my own regression.** While migrating routes from raw `request.form` handling to Flask-WTF, I dropped a security fix I'd already made earlier (hardcoded role) and a field-name bug — caught both by comparing against the working version instead of trusting my rewrite.

## Status

Actively in progress. Auth, models, and full session CRUD are done and tested end-to-end against a live Postgres database. Currently building: aggregate reporting, then deployment.

## Learning context

I'm ~10 weeks into Angela Yu's 100 Days of Code, working toward a Data Analyst role. I use Claude as a mentor throughout this project — hints and concept explanations rather than finished code, code review on what I write myself. The commit history and this file reflect a project still being actively built, not a finished product.
