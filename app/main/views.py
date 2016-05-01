from flask import redirect, url_for, render_template, flash, request, send_file
from flask.ext.login import current_user
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from .forms import ChallengeForm
from . import main
from ..models import Challenge, User


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
            form_challenge = Challenge.objects.get(id=str(form['f'].challenge_submission.name).split('-')[0])

            if form['f'].validate() and \
               form['f'].challenge_submission.data and \
               form['f'].challenge_submission.data != '':

                submission = form['f'].challenge_submission.data.rstrip()

                if form_challenge.id not in current_user.solved_challenges:
                    if form_challenge.fuzzy_answer:
                        ratio = fuzz.token_sort_ratio(form_challenge.plain_text, form['f'].challenge_submission.data)
                        if ratio >= 83:
                            u = User.objects.get(id=current_user.id)
                            u.update(inc__score=form_challenge.points, upsert=True)
                            u.update(push__solved_challenges=form_challenge.id, upsert=True)
                            form_challenge.update(inc__successes=1)
                            flash("Correct!")
                            return redirect(url_for('main.index'))
                        else:
                            form_challenge.update(inc__failures=1)
                            flash("Incorrect!")

                    elif submission == form_challenge.plain_text:
                        u = User.objects.get(id=current_user.id)
                        u.update(inc__score=form_challenge.points, upsert=True)
                        u.update(push__solved_challenges=form_challenge.id, upsert=True)
                        form_challenge.update(inc__successes=1)
                        flash("Correct!")
                        return redirect(url_for('main.index'))
                    else:
                        form_challenge.update(inc__failures=1)
                        flash("Incorrect!")

                else:
                    flash("You've already solved that challenge!")

    return render_template("index.html", challenges=Challenge, forms=forms)


@main.route('/scoreboard')
def scoreboard():
    users = User.objects.order_by('-score')
    return render_template('scoreboard.html', users=users)
