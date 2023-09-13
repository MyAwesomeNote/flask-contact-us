import os

from email_validator import validate_email, EmailNotValidError
from flask import Flask, render_template, request, flash, url_for, redirect
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message


def env(x):
    return os.environ.get(x)


app = Flask(__name__)

# noinspection SpellCheckingInspection
app.config["SECRET_KEY"] = "1NDckZzNTIyNzM1kcHRgfvMpx7"  # os.urandom(24)
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False  # Disable redirect interception

app.config["MAIL_SERVER"] = env("MAIL_SERVER")
app.config["MAIL_PORT"] = env("MAIL_PORT")
app.config["MAIL_USE_TLS"] = env("MAIL_USE_TLS")
app.config["MAIL_USE_SSL"] = env("MAIL_USE_SSL")
app.config["MAIL_USERNAME"] = env("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = env("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = env("MAIL_DEFAULT_SENDER")

mail = Mail(app)
toolbar = DebugToolbarExtension(app)


# noinspection PyUnresolvedReferences
def send_email(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to])

    # template file is exists?
    the_file = f"templates/contact/emails/{template}"
    if not os.path.exists(f"{the_file}.txt") or not os.path.exists(f"{the_file}.html"):
        raise FileNotFoundError(f"Template file not found: {template}")

    msg.body = render_template(f"contact/emails/{template}.txt", **kwargs)
    msg.html = render_template(f"contact/emails/{template}.html", **kwargs)
    mail.send(msg)


@app.route("/", methods=["GET"], endpoint="hello-default-ep")
def root():
    return render_template("hello.html", name="Anon")


@app.route("/<string:name>", methods=["GET"], endpoint="hello-ep")
def user(name: str):
    return render_template("hello.html", name=name)


@app.route("/contact")
def contact():
    return render_template("contact/contact.html")


@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method != "POST":
        return redirect(url_for("contact_complete"))

    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    is_valid = True
    field_of_error = None

    if not name or not message:
        is_valid = False
        field_of_error = "name" if not name else "email" if not email else "message"
        flash(f"Please fill the {field_of_error} field", "error")

    try:
        validate_email(email)
    except EmailNotValidError:
        is_valid = False
        field_of_error = "email"

    if not is_valid:
        flash(f"Please enter a valid {field_of_error}", "error")
        return redirect(url_for("contact"))

    send_email(
        email,
        "Thank you for contacting us!",
        "contact_email",
        name=name,
        message=message
    )

    flash("You are already sent message once over!", "success")
    return render_template("contact/contact_complete.html")
