from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from models import db, Book, Genre, Review, ReviewStatus, Cover
from auth import check_rights
import bleach
import os
import hashlib
from config import Config

books_bp = Blueprint('books', __name__, url_prefix='/books')

# разрешенные теги для санитайзера
ALLOWED_TAGS = ['p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote']

@books_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    books = Book.query.order_by(Book.year.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('books/index.html', books=books)

@books_bp.route('/<int:book_id>')
def view(book_id):
    book = Book.query.get_or_404(book_id)
    approved_reviews = Review.query.filter_by(book_id=book_id).join(ReviewStatus).filter(ReviewStatus.name == 'approved').all()
    
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    
    return render_template('books/view.html', book=book, reviews=approved_reviews, user_review=user_review)

@books_bp.route('/create', methods=['GET', 'POST'])
@check_rights('create_book')
def create():
    genres = Genre.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        year = request.form.get('year', '')
        publisher = request.form.get('publisher', '').strip()
        pages = request.form.get('pages', '')
        description = request.form.get('description', '')
        genre_ids = request.form.getlist('genres')
        
        errors = {}
        
        if not title:
            errors['title'] = 'Название обязательно'
        if not author:
            errors['author'] = 'Автор обязателен'
        if not year or not year.isdigit() or int(year) < 0 or int(year) > 2026:
            errors['year'] = 'Введите корректный год'
        if not publisher:
            errors['publisher'] = 'Издательство обязательно'
        if not pages or not pages.isdigit() or int(pages) <= 0:
            errors['pages'] = 'Введите корректное количество страниц'
        if not description:
            errors['description'] = 'Описание обязательно'
        
        if errors:
            return render_template('books/form.html', 
                                 genres=genres, 
                                 errors=errors, 
                                 form_data=request.form,
                                 title='Добавление книги')
        
        clean_description = bleach.clean(description, tags=ALLOWED_TAGS, strip=True)
        book = Book(
            title=title,
            author=author,
            year=int(year),
            publisher=publisher,
            pages=int(pages),
            description=clean_description
        )
        
        for genre_id in genre_ids:
            genre = Genre.query.get(int(genre_id))
            if genre:
                book.genres.append(genre)
        
        db.session.add(book)
        # временно коммитим, чтобы получить ID книги
        db.session.commit()
        
        # обработка обложки
        cover_file = request.files.get('cover')
        if cover_file and cover_file.filename:
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            
            # вычисляем MD5 хэш файла
            md5 = hashlib.md5(cover_file.read()).hexdigest()
            cover_file.seek(0)
            
            # проверяем, есть ли уже обложка с таким MD5
            existing_cover = Cover.query.filter_by(md5_hash=md5).first()
            
            if existing_cover:
                # если такая обложка уже существует, просто связываем её с текущей книгой
                existing_cover.book_id = book.id
                db.session.commit()
                flash('Книга успешно добавлена! (использована существующая обложка)', 'success')
            else:
                # сохраняем новую обложку
                ext = cover_file.filename.rsplit('.', 1)[1].lower() if '.' in cover_file.filename else 'jpg'
                # используем ID книги как имя файла
                filename = f"{book.id}.{ext}"
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                cover_file.save(filepath)
                
                cover = Cover(
                    filename=filename,
                    mime_type=cover_file.mimetype,
                    md5_hash=md5,
                    book_id=book.id
                )
                db.session.add(cover)
                db.session.commit()
                flash('Книга успешно добавлена!', 'success')
        else:
            flash('Книга успешно добавлена!', 'success')
        
        return redirect(url_for('books.view', book_id=book.id))
    
    return render_template('books/form.html', genres=genres, title='Добавление книги', errors={}, form_data={})

@books_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@check_rights('edit_book')
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    genres = Genre.query.all()

    if request.method == 'POST':
        # валидация данных
        errors = {}
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        year = request.form.get('year', '')
        publisher = request.form.get('publisher', '').strip()
        pages = request.form.get('pages', '')
        description = request.form.get('description', '')

        if not title:
            errors['title'] = 'Название обязательно'
        if not author:
            errors['author'] = 'Автор обязателен'
        if not year or not year.isdigit() or int(year) < 0 or int(year) > 2026:
            errors['year'] = 'Введите корректный год'
        if not publisher:
            errors['publisher'] = 'Издательство обязательно'
        if not pages or not pages.isdigit() or int(pages) <= 0:
            errors['pages'] = 'Введите корректное количество страниц'
        if not description:
            errors['description'] = 'Описание обязательно'

        if errors:
            form_data = {
                'title': title,
                'author': author,
                'publisher': publisher,
                'year': year,
                'pages': pages,
                'description': description,
                'genres': request.form.getlist('genres')
            }
            return render_template('books/form.html',
                                 genres=genres,
                                 errors=errors,
                                 form_data=form_data,
                                 is_edit=True,
                                 title='Редактирование книги')

        clean_description = bleach.clean(description, tags=ALLOWED_TAGS, strip=True)
        book.title = title
        book.author = author
        book.year = int(year)
        book.publisher = publisher
        book.pages = int(pages)
        book.description = clean_description

        genre_ids = request.form.getlist('genres')
        book.genres = []
        for genre_id in genre_ids:
            genre = Genre.query.get(int(genre_id))
            if genre:
                book.genres.append(genre)

        try:
            db.session.commit()
            flash('Книга успешно обновлена!', 'success')
            return redirect(url_for('books.view', book_id=book.id))
        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('books/form.html',
                                 genres=genres,
                                 form_data=request.form,
                                 is_edit=True,
                                 title='Редактирование книги')

    form_data = {
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'year': book.year,
        'publisher': book.publisher,
        'pages': book.pages,
        'description': book.description,
        'genres': [str(g.id) for g in book.genres]
    }

    return render_template('books/form.html',
                     genres=genres,
                     form_data=form_data,
                     errors={},
                     is_edit=True,
                     title='Редактирование книги')

@books_bp.route('/<int:book_id>/delete', methods=['POST'])
@check_rights('delete_book')
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    title = book.title
    
    if book.cover:
        cover_path = os.path.join(Config.UPLOAD_FOLDER, book.cover.filename)
        if os.path.exists(cover_path):
            os.remove(cover_path)
    
    db.session.delete(book)
    db.session.commit()
    
    flash(f'Книга "{title}" успешно удалена!', 'success')
    return redirect(url_for('books.index'))