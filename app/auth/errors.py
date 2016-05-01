from flask import render_template, redirect, url_for
from . import auth


@auth.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@auth.app_errorhandler(500)
def server_error(e):
    return redirect(url_for('..views/index'))
