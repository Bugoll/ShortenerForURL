
import qrcode, random, string, os, pyperclip
from shortener import app, db
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, abort, jsonify
from flask import render_template, send_file
from shortener.models import User, Link
from shortener.forms import RegisterForm, ShortenLinkForm, LoginForm, PersonalShortenLinkForm
from flask_login import login_user, logout_user, login_required, current_user
import time
now_timestamp = int(time.time())


def generate_short_link(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@app.route('/<short_url>')
def redirect_to_original(short_url):
    link = Link.query.filter_by(short_url=short_url).first()
    
    if link:
        return redirect(link.original_url)  # Redirect to the original URL
    else:
        abort(404)  # If the link is not found, return a 404 error


@app.route('/copy', methods=['POST'])
def copy_to_clipboard():
    short_link = request.form.get('short_link')  # Получаем ссылку из формы

    if not short_link:
        flash("No link provided!", "danger")
        return redirect(url_for("home_page"))  # Перенаправляем обратно
    


    pyperclip.copy(short_link)  # Копируем в буфер обмена на сервере
    flash("Link copied to clipboard!", "success")

    return redirect(url_for("home_page"))  # Возвращаем пользователя обратно


@app.route('/personalcopy', methods=['POST'])
def personal_copy_to_clipboard():
    personal_short_link = request.form.get('short_link')  # Получаем ссылку из формы

    if not personal_short_link:
        flash("No link provided!", "danger")
        return redirect(url_for("personal_page"))  # Перенаправляем обратно
    


    pyperclip.copy(personal_short_link)  # Копируем в буфер обмена на сервере
    flash("Link copied to clipboard!", "success")

    return redirect(url_for("personal_page"))  # Возвращаем пользователя обратно



@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home_page():
    form = ShortenLinkForm()
    short_link_url = None

    if form.validate_on_submit():
        original_url = form.destination_link.data
        short_url = generate_short_link()

        new_link = Link(original_url=original_url, short_url=short_url)  # Use original_url instead of long_url
        db.session.add(new_link)
        db.session.commit()

        short_link_url = request.host_url + short_url
        form.shortened_link.data = short_link_url
        flash('Your link was shortened successfully!', 'success')

        return render_template('home.html', form=form, short_link=short_link_url)

    return render_template('home.html', form=form)


@app.route('/personal', methods=['GET', 'POST'])
@login_required
def personal_page():
    personal_form = PersonalShortenLinkForm()
    short_link = None
    qr_code_path = None

    # Fetch all links for the current user
    items = Link.query.filter_by(user_id=current_user.id).all()

    if personal_form.validate_on_submit():
        # Get the original URL from the form
        original_url = personal_form.personaldestination_link.data
        # Generate a short URL
        short_url = generate_short_link()
        

        # Create a new Link object and save it to the database
        new_link = Link(original_url=original_url, short_url=short_url, user_id=current_user.id)
        db.session.add(new_link)
        db.session.commit()

        short_link = request.host_url + short_url
        personal_form.personalshortened_link.data = short_link

        # Generate a QR code for the shortened link
        qr_code_img = qrcode.make(short_link)
        qr_code_filename = f'{short_url}.png'

        # Save the QR code in the static/qr_codes directory inside the shortener folder
        qr_code_full_path = os.path.join(app.root_path, 'static', 'qr_codes', qr_code_filename)
        os.makedirs(os.path.dirname(qr_code_full_path), exist_ok=True)  # Ensure the directory exists
        qr_code_img.save(qr_code_full_path)

        # Pass the relative path to the template
        qr_code_path = os.path.join('qr_codes', qr_code_filename)

        


        # Flash a success message
        flash('Your link was shortened successfully!', 'success')

        return render_template('personal.html', personal_form=personal_form, items=items, short_link=short_link, qr_code_path=qr_code_path, now_timestamp=now_timestamp)

    # Render the personal.html template with the form, items, and short_link
    return render_template('personal.html', personal_form=personal_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                            password=(form.password1.data))
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as: {user_to_create.username}', category='success')
        
        return redirect(url_for('personal_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('personal_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for('home_page'))

