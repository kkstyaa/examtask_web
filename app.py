from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'

# Регистрация Blueprint'ов
from books import books_bp
from reviews import reviews_bp

app.register_blueprint(books_bp)
app.register_blueprint(reviews_bp)

import markdown
from bleach import clean

#допустимые теги для безопасности
ALLOWED_TAGS = ['p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'br']

@app.template_filter('markdown')
def markdown_filter(text):
    """Преобразует Markdown в безопасный HTML"""
    if not text:
        return ''
    # конвертируем markdown в HTML
    html = markdown.markdown(text, extensions=['extra', 'codehilite'])
    #очищаем от опасных тегов
    clean_html = clean(html, tags=ALLOWED_TAGS, strip=True)
    return clean_html

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ГЛАВНАЯ СТРАНИЦА
@app.route('/')
def index():
    return redirect(url_for('books.index'))

# АУТЕНТИФИКАЦИЯ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        login_name = request.form.get('login')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.filter_by(login=login_name).first()
        
        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Невозможно аутентифицироваться с указанными логином и паролем.', 'danger')
    
    return render_template('login.html', title='Вход')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)