from flask import redirect, url_for, render_template, flash, request
from flask.ext.login import current_user
from fuzzywuzzy import fuzz
from .forms import ChallengeForm
from . import main
from ..models import Challenge, User, Audit


@main.route('/', methods=['GET', 'POST'])
def index():
    forms = []
    for challenge in Challenge.objects(active=True):
        solved = False
        if current_user.is_authenticated and \
           challenge.id in current_user.solved_challenges:
            solved = True

        form = {'f': ChallengeForm(prefix=str(challenge.id)),
                'challenge_text': challenge.challenge_text,
                'points': challenge.points,
                'attachment_path': challenge.attachment_path,
                'successes': challenge.successes,
                'failures': challenge.failures,
                'solved': solved}
        forms.append(form)
    if request.method == "POST":

        if not current_user.is_authenticated:
            flash('You must be logged in to submit challenges')
            return redirect(url_for('main.index'))

        for form in forms:
            form_c = Challenge.objects.get(id=str(form['f'].challenge_submission.name).split('-')[0])

            if form['f'].challenge_submission.data and \
               form['f'].challenge_submission.data != '' and \
               form['f'].validate():

                a = Audit(user=current_user.username,
                          message_type="user",
                          ip=request.remote_addr)
                submission = form['f'].challenge_submission.data.rstrip()

                if form_c.id not in current_user.solved_challenges:
                    if not form_c.case_sensitive:
                        submission = submission.lower()

                    if form_c.fuzzy_answer:
                        ratio = fuzz.token_sort_ratio(form_c.plain_text, form['f'].challenge_submission.data)
                        if ratio >= 83:
                            u = User.objects.get(id=current_user.id)
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

    return render_template("index.html", challenges=Challenge, forms=forms)


@main.route('/scoreboard')
def scoreboard():
    users = User.objects.order_by('-score')
    return render_template('scoreboard.html', users=users)
