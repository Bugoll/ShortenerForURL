import qrcode, random, string, os
from shortener import app
from flask import Flask, render_template, request, redirect, url_for, flash, session
from shortener.forms import RegisterForm

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_qr_code(short_url):
    img = qrcode.make(short_url)
    img_path = f'static/qrcodes/{short_url}.png'
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    img.save(img_path)
    return img_path

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    return render_template('register.html', form=form)

@app.route('/login', endpoint='login', methods=['GET', 'POST'])
def login_page():
    pass

@app.route('/logout', endpoint='logout', methods=['GET', 'POST'])
def logout_page():
    pass
   