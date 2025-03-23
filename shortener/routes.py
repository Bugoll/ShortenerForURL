import qrcode, random, string, os, pyperclip
from shortener import app, db
from flask import render_template, request, redirect, url_for, flash, abort
from shortener.models import User, Link
from shortener.forms import RegisterForm, ShortenLinkForm, LoginForm, PersonalShortenLinkForm
from flask_login import login_user, logout_user, login_required, current_user
import time

now_timestamp = int(time.time())

# Очистка осиротевших QR-кодов при запуске
def cleanup_orphan_qr_codes():
    print("🔄 Очистка осиротевших QR-кодов...")
    qr_codes_root = os.path.join(app.root_path, 'static', 'qr_codes')
    if not os.path.isdir(qr_codes_root):
        return

    for user_folder in os.listdir(qr_codes_root):
        user_folder_path = os.path.join(qr_codes_root, user_folder)
        if not os.path.isdir(user_folder_path):
            continue

        for qr_file in os.listdir(user_folder_path):
            if qr_file.endswith('.png'):
                short_code = qr_file[:-4]
                if not Link.query.filter_by(short_url=short_code).first():
                    qr_path = os.path.join(user_folder_path, qr_file)
                    try:
                        os.remove(qr_path)
                        print(f"🗑️ Удалён: {qr_path}")
                    except Exception as e:
                        print(f"❌ Ошибка удаления {qr_path}: {e}")

# Очистка один раз перед первым запросом
cleanup_done = False

@app.before_request
def cleanup_once():
    global cleanup_done
    if not cleanup_done:
        cleanup_orphan_qr_codes()
        cleanup_done = True

# Очистка при старте сервера
with app.app_context():
    cleanup_orphan_qr_codes()

# Генерация короткой ссылки
def generate_short_link(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/<short_url>')
def redirect_to_original(short_url):
    link = Link.query.filter_by(short_url=short_url).first()
    return redirect(link.original_url) if link else abort(404)

@app.route('/copy', methods=['POST'])
def copy_to_clipboard():
    short_link = request.form.get('short_link')
    if short_link:
        pyperclip.copy(short_link)
        flash("Link copied to clipboard!", "success")
    else:
        flash("No link provided!", "danger")
    return redirect(url_for("home_page"))

@app.route('/personalcopy', methods=['POST'])
def personal_copy_to_clipboard():
    short_link = request.form.get('short_link')
    if short_link:
        pyperclip.copy(short_link)
        flash("Link copied to clipboard!", "success")
    else:
        flash("No link provided!", "danger")
    return redirect(url_for("personal_page"))

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home_page():
    form = ShortenLinkForm()
    if form.validate_on_submit():
        short_url = generate_short_link()
        new_link = Link(original_url=form.destination_link.data, short_url=short_url)
        db.session.add(new_link)
        db.session.commit()

        full_short_link = request.host_url + short_url
        form.shortened_link.data = full_short_link
        flash('Your link was shortened successfully!', 'success')
        return render_template('home.html', form=form, short_link=full_short_link)

    return render_template('home.html', form=form)

@app.route('/personal', methods=['GET', 'POST'])
@login_required
def personal_page():
    form = PersonalShortenLinkForm()
    short_link, qr_code_path = None, None

    # Получаем 5 последних ссылок
    links = Link.query.filter_by(user_id=current_user.id).order_by(Link.id.desc()).limit(5).all()

    if form.validate_on_submit():
        # Удаляем самую старую ссылку, если уже 5
        all_links = Link.query.filter_by(user_id=current_user.id).order_by(Link.id.asc()).all()
        if len(all_links) >= 5:
            old_link = all_links[0]
            qr_folder = os.path.join(app.root_path, 'static', 'qr_codes', str(current_user.id))
            qr_path = os.path.join(qr_folder, f"{old_link.short_url}.png")
            if os.path.exists(qr_path):
                os.remove(qr_path)
            db.session.delete(old_link)
            db.session.commit()

        # Генерация новой ссылки и QR
        short_url = generate_short_link()
        new_link = Link(original_url=form.personaldestination_link.data, short_url=short_url, user_id=current_user.id)
        db.session.add(new_link)
        db.session.commit()

        full_short_link = request.host_url + short_url
        form.personalshortened_link.data = full_short_link

        qr_folder = os.path.join(app.root_path, 'static', 'qr_codes', str(current_user.id))
        os.makedirs(qr_folder, exist_ok=True)
        qr_filename = f"{short_url}.png"
        qr_full_path = os.path.join(qr_folder, qr_filename)
        qrcode.make(full_short_link).save(qr_full_path)
        qr_code_path = os.path.join('qr_codes', str(current_user.id), qr_filename)

        flash('Your link was shortened successfully!', 'success')

        # Обновляем список и удаляем лишние QR
        links = Link.query.filter_by(user_id=current_user.id).order_by(Link.id.desc()).limit(5).all()
        valid_codes = {link.short_url for link in links}
        for file in os.listdir(qr_folder):
            if file.endswith('.png') and file[:-4] not in valid_codes:
                try:
                    os.remove(os.path.join(qr_folder, file))
                    print(f"🗑️ Лишний QR удалён: {file}")
                except Exception as e:
                    print(f"❌ Ошибка удаления {file}: {e}")

        return render_template('personal.html', personal_form=form, items=links, short_link=full_short_link, qr_code_path=qr_code_path, now_timestamp=int(time.time()))

    return render_template('personal.html', personal_form=form, items=links, short_link=short_link, qr_code_path=qr_code_path, now_timestamp=int(time.time()))

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password1.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Registration successful! Logged in as: {user.username}', 'success')
        return redirect(url_for('personal_page'))
    for errors in form.errors.values():
        flash(f'Error: {errors}', 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password_correction(form.password.data):
            login_user(user)
            flash(f'Logged in as: {user.username}', 'success')
            return redirect(url_for('personal_page'))
        flash('Invalid credentials. Try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('Logged out!', 'info')
    return redirect(url_for('home_page'))
