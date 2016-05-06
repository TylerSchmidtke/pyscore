from flask import redirect, url_for, render_template, flash, request
from flask.ext.bcrypt import generate_password_hash
from passlib import hash
from . import admin
from ..models import Challenge, User
from .forms import CreateChallengeForm, ModifyChallengeForm, SearchUserForm, ModifyUserForm
from ..decorators import role_required
from .. import attachments
import os


@admin.route('/challenges/create', methods=['GET', 'POST'])
@role_required('administrator')
def create_challenge():
    form = CreateChallengeForm()
    if form.validate_on_submit():
        if form.hash_type.data:
            hasher = getattr(hash, form.hash_type.data)
            form.challenge_text.data = hasher.encrypt(form.plain_text.data.rstrip())
            if form.notes.data:
                form.notes.data = "Hash Type: {} // {}".format(form.hash_type.data, form.notes.data)
            else:
                form.notes.data = form.hash_type.data
        if not form.case_sensitive.data:
            form.plain_text.data = form.plain_text.data.rstrip().l
        challenge = Challenge(plain_text=form.plain_text.data.rstrip(),
                              challenge_text=form.challenge_text.data.rstrip(),
                              notes=form.notes.data,
                              points=form.points.data,
                              active=form.active.data,
                              case_sensitive=form.case_sensitive.data,
                              fuzzy_answer=form.fuzzy_answer.data)
        challenge.save()
        if request.files['attachment']:
            filename = attachments.save(request.files['attachment'])
            challenge.attachment_path = filename
            challenge.save()
        flash("Challenge created.")
        return redirect(url_for('admin.create_challenge'))
    return render_template('admin/challenge/create.html', form=form)


@admin.route('/challenges')
@role_required('administrator')
def list_challenges():
    c = Challenge.objects()
    return render_template('admin/challenge/list.html', challenges=c)


@admin.route('/challenges/modify/<challenge_id>', methods=['GET', 'POST'])
@role_required('administrator')
def modify_challenge(challenge_id):
    c = Challenge.objects.get(id=challenge_id)
    form = ModifyChallengeForm()
    if request.method == 'GET':
        form.active.data = c.active
        form.points.data = c.points
        form.fuzzy_answer.data = c.fuzzy_answer

    if form.validate_on_submit():
        if form.delete.data:
            # Delete challenge from all users, adjust their score,
            # and delete the challenge
            User.objects(solved_challenges__contains=c.id).update(inc__score=-c.points)
            User.objects(solved_challenges__contains=c.id).update(pull__solved_challenges=c)
            if c.attachment_path and \
                    os.path.isfile('app/static/attachments/' + c.attachment_path):
                os.remove('app/static/attachments/' + c.attachment_path)

            flash('Challenge Deleted.')
            c.delete()
            return redirect(url_for('admin.list_challenges'))
        if form.points.data != c.points:
            c.update(set__points=form.points.data)
            flash('Updated Points.')
        if form.active.data != c.active:
            c.update(set__active=form.active.data)
            if form.active.data:
                flash('Activated Challenge.')
            else:
                flash('Deactivated Challenge.')
        if form.fuzzy_answer.data != c.fuzzy_answer:
            c.update(set__fuzzy_answer=form.fuzzy_answer.data)
            if form.fuzzy_answer.data:
                flash('Challenge now accepts fuzzy answers.')
            else:
                flash('Challenge no longer accepts fuzzy answers.')

        # Check for new attachment and update, deleting old attachment
        if request.files['attachment']:
            if c.attachment_path and \
                    os.path.isfile('app/static/attachments/' + c.attachment_path):
                os.remove('app/static/attachments/' + c.attachment_path)
            filename = attachments.save(request.files['attachment'])
            c.update(set__attachment_path=filename)
            flash('Updated Attachment.')

        return redirect(url_for('admin.list_challenges'))
    return render_template('admin/challenge/modify.html', challenge=c, form=form)


@admin.route('/users/search', methods=['GET', 'POST'])
@role_required('administrator')
def user_search():
    form = SearchUserForm()
    if request.method == 'POST':
        u = User.objects(roles=form.role.data).exclude('password_hash', 'id')
        return render_template('admin/user/list.html', users=u)
    return render_template('admin/user/search.html', form=form)


@admin.route('/users')
@role_required('administrator')
def list_users():
    u = User.objects()
    return render_template('admin/user/list.html', users=u)


@admin.route('/users/<user>', methods=['GET', 'POST'])
@role_required('administrator')
def user_modify(user):
    form = ModifyUserForm()
    u = User.objects(username=user).first()
    if form.validate_on_submit():
        if form.delete.data:
            u.delete()
            flash('User Deleted.')
            return redirect(url_for('admin.list_users'))
        if form.password.data != '':
            # Not sure why this is returned as a byte array, convert to utf-8
            u.update(set__password_hash=generate_password_hash(form.password.data, rounds=15).decode('utf-8'))
            flash('Password updated!')
        if form.score.data:
            u.update(set__score=form.score.data)
            flash('Score updated')
    return render_template('admin/user/modify.html', user=u, form=form)
