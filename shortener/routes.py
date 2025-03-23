import qrcode, random, string, os, pyperclip
from shortener import app, db
from flask import render_template, request, redirect, url_for, flash, abort
from shortener.models import User, Link
from shortener.forms import RegisterForm, ShortenLinkForm, LoginForm, PersonalShortenLinkForm
from flask_login import login_user, logout_user, login_required, current_user
import time

# Текущий timestamp для кеш-бастинга QR-кодов
now_timestamp = int(time.time())

# ⬇️ Очистка осиротевших QR-кодов при запуске
def cleanup_orphan_qr_codes():
    print("🔄 Очистка осиротевших QR-кодов...")
    qr_codes_root = os.path.join(app.root_path, 'static', 'qr_codes')

    if not os.path.exists(qr_codes_root):
        print("📁 Папка qr_codes отсутствует.")
        return

    for user_id_folder in os.listdir(qr_codes_root):
        user_folder_path = os.path.join(qr_codes_root, user_id_folder)
        if not os.path.isdir(user_folder_path):
            continue

        for qr_file in os.listdir(user_folder_path):
            if qr_file.endswith('.png'):
                short_url_candidate = qr_file.replace('.png', '')
                link = Link.query.filter_by(short_url=short_url_candidate).first()

                if not link:
                    qr_path_to_remove = os.path.join(user_folder_path, qr_file)
                    try:
                        os.remove(qr_path_to_remove)
                        print(f"🗑️ Удалён: {qr_path_to_remove}")
                    except Exception as e:
                        print(f"❌ Ошибка удаления {qr_path_to_remove}: {e}")

# Очистка выполняется один раз при первом запросе
cleanup_done = False

@app.before_request
def cleanup_once_before_first_request():
    global cleanup_done
    if not cleanup_done:
        cleanup_orphan_qr_codes()
        cleanup_done = True

# Запускаем очистку при старте сервера
with app.app_context():
    cleanup_orphan_qr_codes()

# Генерация короткой ссылки
def generate_short_link(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/<short_url>')
def redirect_to_original(short_url):
    link = Link.query.filter_by(short_url=short_url).first()
    if link:
        return redirect(link.original_url)
    else:
        abort(404)

@app.route('/copy', methods=['POST'])
def copy_to_clipboard():
    short_link = request.form.get('short_link')
    if not short_link:
        flash("No link provided!", "danger")
        return redirect(url_for("home_page"))
    pyperclip.copy(short_link)
    flash("Link copied to clipboard!", "success")
    return redirect(url_for("home_page"))

@app.route('/personalcopy', methods=['POST'])
def personal_copy_to_clipboard():
    personal_short_link = request.form.get('short_link')
    if not personal_short_link:
        flash("No link provided!", "danger")
        return redirect(url_for("personal_page"))
    pyperclip.copy(personal_short_link)
    flash("Link copied to clipboard!", "success")
    return redirect(url_for("personal_page"))

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home_page():
    form = ShortenLinkForm()
    short_link_url = None
    if form.validate_on_submit():
        original_url = form.destination_link.data
        short_url = generate_short_link()
        new_link = Link(original_url=original_url, short_url=short_url)
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

    # Загружаем последние 5 ссылок пользователя
    items = Link.query.filter_by(user_id=current_user.id).order_by(Link.id.desc()).limit(5).all()

    if personal_form.validate_on_submit():
        # Удаление старой ссылки, если уже 5 (оставляем только 4 и добавляем новую)
        user_links_all = Link.query.filter_by(user_id=current_user.id).order_by(Link.id.asc()).all()
        if len(user_links_all) >= 5:
            oldest_link = user_links_all[0]
            qr_filename_old = f"{oldest_link.short_url}.png"
            qr_folder_old = os.path.join(app.root_path, 'static', 'qr_codes', str(current_user.id))
            qr_full_path_old = os.path.join(qr_folder_old, qr_filename_old)

            print(f"📎 short_url старой ссылки: {oldest_link.short_url}")
            print(f"Попытка удалить QR старой ссылки: {qr_full_path_old}")

            if os.path.exists(qr_folder_old):
                print(f"📁 Файлы в папке {qr_folder_old}:")
                for file in os.listdir(qr_folder_old):
                    print(f" - {file}")
            else:
                print(f"❗ Папка {qr_folder_old} не найдена.")

            if os.path.exists(qr_full_path_old):
                try:
                    os.remove(qr_full_path_old)
                    print(f"✅ Старый QR удалён: {qr_full_path_old}")
                except Exception as e:
                    print(f"❌ Ошибка удаления QR: {e}")
            else:
                print(f"❗ Файл {qr_full_path_old} не найден для удаления.")

            db.session.delete(oldest_link)
            db.session.commit()

        # Генерация новой ссылки
        original_url = personal_form.personaldestination_link.data
        short_url = generate_short_link()
        new_link = Link(original_url=original_url, short_url=short_url, user_id=current_user.id)
        db.session.add(new_link)
        db.session.commit()

        short_link = request.host_url + short_url
        personal_form.personalshortened_link.data = short_link

        # Генерация QR-кода
        qr_code_img = qrcode.make(short_link)
        qr_folder = os.path.join(app.root_path, 'static', 'qr_codes', str(current_user.id))
        os.makedirs(qr_folder, exist_ok=True)

        qr_code_filename = f'{short_url}.png'
        qr_code_full_path = os.path.join(qr_folder, qr_code_filename)
        qr_code_img.save(qr_code_full_path)
        print(f"✅ QR-код сохранён: {qr_code_full_path}")

        qr_code_path = os.path.join('qr_codes', str(current_user.id), qr_code_filename)

        flash('Your link was shortened successfully!', 'success')

        # Обновить список ссылок после добавления новой
        items = Link.query.filter_by(user_id=current_user.id).order_by(Link.id.desc()).limit(5).all()

        # Очистка лишних QR-кодов, которые не входят в список 5 ссылок
        valid_short_urls = {link.short_url for link in items}
        for qr_file in os.listdir(qr_folder):
            if qr_file.endswith('.png'):
                short_url_candidate = qr_file.replace('.png', '')
                if short_url_candidate not in valid_short_urls:
                    qr_path_to_remove = os.path.join(qr_folder, qr_file)
                    try:
                        os.remove(qr_path_to_remove)
                        print(f"🗑️ Лишний QR удалён: {qr_path_to_remove}")
                    except Exception as e:
                        print(f"❌ Ошибка удаления лишнего QR {qr_path_to_remove}: {e}")

        return render_template('personal.html', personal_form=personal_form, items=items, short_link=short_link, qr_code_path=qr_code_path, now_timestamp=int(time.time()))

    return render_template('personal.html', personal_form=personal_form, items=items, short_link=short_link, qr_code_path=qr_code_path, now_timestamp=int(time.time()))

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as: {user_to_create.username}', category='success')
        return redirect(url_for('personal_page'))
    if form.errors != {}:
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
