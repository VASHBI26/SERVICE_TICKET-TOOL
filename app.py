from flask import Flask, render_template, request, redirect, session, url_for
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy data stores
users = {'admin': {'password': 'admin123', 'role': 'admin'}}
tickets = []
audit_logs = []

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = users.get(uname)
        if user and user['password'] == pwd:
            session['user'] = uname
            session['role'] = user['role']
            audit_logs.append(f"{datetime.now()} - {uname} logged in.")
            return redirect(url_for(f"{user['role']}_dashboard"))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    uname = session.get('user', 'Unknown')
    audit_logs.append(f"{datetime.now()} - {uname} logged out.")
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', users=users, logs=audit_logs)

@app.route('/admin/create_user', methods=['POST'])
def create_user():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    uname = request.form['username']
    pwd = request.form['password']
    role = request.form['role']
    users[uname] = {'password': pwd, 'role': role}
    audit_logs.append(f"{datetime.now()} - Admin created user {uname} with role {role}.")
    return redirect(url_for('admin_dashboard'))

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    user_tickets = [t for t in tickets if t['created_by'] == session['user']]
    return render_template('user_dashboard.html', tickets=user_tickets)

@app.route('/user/create_ticket', methods=['POST'])
def create_ticket():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    ticket = {
        'id': len(tickets) + 1,
        'created_by': session['user'],
        'type': request.form['type'],
        'description': request.form['description'],
        'status': 'Pending'
    }
    tickets.append(ticket)
    audit_logs.append(f"{datetime.now()} - Ticket #{ticket['id']} created by {session['user']}.")
    return redirect(url_for('user_dashboard'))

@app.route('/approver/dashboard')
def approver_dashboard():
    if session.get('role') != 'approver':
        return redirect(url_for('login'))
    return render_template('approver_dashboard.html', tickets=tickets)

@app.route('/approver/approve/<int:ticket_id>')
def approve_ticket(ticket_id):
    if session.get('role') != 'approver':
        return redirect(url_for('login'))
    for t in tickets:
        if t['id'] == ticket_id:
            t['status'] = 'Approved'
            audit_logs.append(f"{datetime.now()} - Ticket #{ticket_id} approved by {session['user']}.")
    return redirect(url_for('approver_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
