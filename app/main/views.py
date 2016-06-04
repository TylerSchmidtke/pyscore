from flask import redirect, url_for, render_template, flash, request
from flask.ext.login import current_user
from fuzzywuzzy import fuzz
from .forms import ChallengeForm, HintForm
from . import main
from ..models import Challenge, User, Audit
import collections


@main.route('/', methods=['GET', 'POST'])
def index():

    # Build an OrderedDict of forms for each challenge.
    # This should work because there should never be duplicate challenge IDs.
    # Associate challenge details with the form
    forms = collections.OrderedDict()

    for challenge in Challenge.objects(active=True):
        solved = False

        if current_user.is_authenticated and challenge.id in current_user.solved_challenges:
            solved = True

        forms[str(challenge.id)] = {
            'f': ChallengeForm(prefix=str(challenge.id)),
            'challenge_text': challenge.challenge_text,
            'challenge_id': challenge.id,
            'points': challenge.points,
            'hint': challenge.hint,
            'hint_points': challenge.hint_points,
            'hint_form': HintForm(prefix=str(challenge.id) + "-hint"),
            'attachment_path': challenge.attachment_path,
            'successes': challenge.successes,
            'failures': challenge.failures,
            'solved': solved,
            'user_hints': current_user.hints
        }

    # Check the submission
    if request.method == "POST":

        if not current_user.is_authenticated:
            flash('You must be logged in to submit challenges')
            return redirect(url_for('main.index'))

        # Grab the first key in the POST form data to lookup the challenge and process the submission
        print(next(request.form.keys()).split('-')[0])
        c_id = str(next(request.form.keys()).split('-')[0])
        form_c = Challenge.objects.get(id=c_id)
        sub_form = forms[c_id]

        # Check if submission is for a hint
        if (c_id + "-hint-submit") in request.form and \
           form_c.id not in sub_form['user_hints']:

            u = User.objects.get(id=current_user.id)
            u.update(push__hints=form_c.id)
            flash("Activated hint.")
            return redirect(url_for('main.index'))

        # Check the submission data
        if sub_form['f'].challenge_submission.data and \
           sub_form['f'].challenge_submission.data != '' and \
           sub_form['f'].validate():
            a = Audit(user=current_user.username,
                      message_type="user",
                      ip=request.remote_addr)
            submission = sub_form['f'].challenge_submission.data.rstrip()

            # Verify the user hasn't solved the challenge and check the submission
            if form_c.id not in current_user.solved_challenges:
                if not form_c.case_sensitive:
                    submission = submission.lower()

                if form_c.fuzzy_answer:
                    ratio = fuzz.token_sort_ratio(form_c.plain_text, sub_form['f'].challenge_submission.data)
                    if ratio >= 83:
                        u = User.objects.get(id=current_user.id)

                        # check if hint was used
                        if form_c.id in current_user.hints:
                            u.update(inc__score=form_c.points - form_c.hint_points, upsert=True)
                        else:
                            u.update(inc__score=form_c.points, upsert=True)

                        u.update(push__solved_challenges=form_c.id, upsert=True)
                        form_c.update(inc__successes=1)
                        flash("Correct!")
                        a.message = "Solved " + str(form_c.id) + " (fuzzy) with a ratio of " + str(ratio)
                        a.save()
                        return redirect(url_for('main.index'))
                    else:
                        form_c.update(inc__failures=1)
                        flash("Incorrect!")
                        a.message = "Failed to solve " + str(form_c.id) + " (fuzzy) with a ratio of " + str(ratio)
                        a.save()

                elif submission == form_c.plain_text:
                    u = User.objects.get(id=current_user.id)

                    # check if hint was used
                    if form_c.id in current_user.hints:
                        u.update(inc__score=form_c.points - form_c.hint_points, upsert=True)
                    else:
                        u.update(inc__score=form_c.points, upsert=True)

                    u.update(push__solved_challenges=form_c.id, upsert=True)
                    form_c.update(inc__successes=1)
                    flash("Correct!")

                    a.message = "Solved " + str(form_c.id)
                    a.save()
                    return redirect(url_for('main.index'))
                else:
                    form_c.update(inc__failures=1)
                    flash("Incorrect!")
                    a.message = "Failed to solve " + str(form_c.id)
                    a.save()
            else:
                a.message = "Tried to solve " + str(form_c.id) + "again."
                a.save()
                flash("You've already solved that challenge!")

    return render_template("index.html", forms=forms)


@main.route('/scoreboard')
def scoreboard():

    # Exclude builtin admin
    users = User.objects.filter(username__ne='admin').order_by('-score')
    return render_template('scoreboard.html', users=users)
