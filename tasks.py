from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from model import db, Task
from datetime import datetime

tasks = Blueprint('tasks', __name__)

# Dashboard - Show tasks
@tasks.route('/')
@login_required
def dashboard():
    search_query = request.args.get('search')
    if search_query:
        tasks_list = Task.query.filter(Task.user_id == current_user.id, Task.title.ilike(f'%{search_query}%')).all()
    else:
        tasks_list = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()

    total = len(tasks_list)
    completed = len([t for t in tasks_list if t.completed])
    return render_template('index.html', tasks=tasks_list, total=total, completed=completed)


# Add a task
@tasks.route('/add', methods=['POST'])
@login_required
def add_task():
    title = request.form['title']
    due_date = request.form.get('due_date')

    if not title:
        flash('Task cannot be empty.', 'error')
        return redirect(url_for('tasks.dashboard'))

    task = Task(title=title, user_id=current_user.id)

    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'error')

    db.session.add(task)
    db.session.commit()
    flash('Task added!', 'success')
    return redirect(url_for('tasks.dashboard'))


# Mark as complete
@tasks.route('/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("You don't have permission to complete this task.", 'error')
        return redirect(url_for('tasks.dashboard'))

    task.completed = True
    db.session.commit()
    flash('Task marked as complete!', 'success')
    return redirect(url_for('tasks.dashboard'))


# Delete a task
@tasks.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("You can't delete someone else's task.", 'error')
        return redirect(url_for('tasks.dashboard'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted!', 'info')
    return redirect(url_for('tasks.dashboard'))


# Edit a task
@tasks.route('/edit/<int:task_id>', methods=['POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("You can't edit someone else's task.", 'error')
        return redirect(url_for('tasks.dashboard'))

    new_title = request.form['title']
    new_due = request.form.get('due_date')

    if new_title:
        task.title = new_title
    if new_due:
        try:
            task.due_date = datetime.strptime(new_due, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format.', 'error')
    db.session.commit()
    flash('Task updated.', 'success')
    return redirect(url_for('tasks.dashboard'))
