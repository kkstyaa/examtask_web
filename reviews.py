from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from models import db, Review, ReviewStatus, Book
from auth import check_rights
import bleach

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

ALLOWED_TAGS = ['p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote']


@reviews_bp.route('/book/<int:book_id>/create', methods=['GET', 'POST'])
@login_required
def create(book_id):
    book = Book.query.get_or_404(book_id)

    existing_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if existing_review:
        flash('Вы уже оставляли рецензию на эту книгу', 'warning')
        return redirect(url_for('books.view', book_id=book_id))

    if request.method == 'POST':
        rating = request.form.get('rating')
        text = request.form.get('text', '')
        
        #валидация
        errors = {}
        if not rating or not rating.isdigit():
            errors['rating'] = 'Пожалуйста, выберите оценку'
        if not text or not text.strip():
            errors['text'] = 'Текст рецензии не может быть пустым'
        
        if errors:
            flash('Пожалуйста, исправьте ошибки в форме', 'danger')
            return render_template('reviews/form.html', book=book, title='Новая рецензия', errors=errors, form_data=request.form)
        
        rating = int(rating)
        clean_text = bleach.clean(text, tags=ALLOWED_TAGS, strip=True)
        pending_status = ReviewStatus.query.filter_by(name='pending').first()

        review = Review(
            rating=rating,
            text=clean_text,
            book_id=book_id,
            user_id=current_user.id,
            status_id=pending_status.id
        )

        try:
            db.session.add(review)
            db.session.commit()
            flash('Рецензия отправлена на модерацию', 'success')
            return redirect(url_for('books.view', book_id=book_id))
        except Exception as e:
            db.session.rollback()
            flash('При сохранении рецензии возникла ошибка. Попробуйте снова.', 'danger')
            return render_template('reviews/form.html', book=book, title='Новая рецензия', form_data=request.form)

    return render_template('reviews/form.html', book=book, title='Новая рецензия', errors={}, form_data={})


@reviews_bp.route('/my')
@login_required
def my_reviews():
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('reviews/my.html', reviews=reviews, title='Мои рецензии')


@reviews_bp.route('/moderate')
@check_rights('moderate_reviews')
def moderate():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pending_status = ReviewStatus.query.filter_by(name='pending').first()
    reviews = Review.query.filter_by(status_id=pending_status.id) \
        .order_by(Review.created_at.asc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template('reviews/moderate.html', reviews=reviews, title='Модерация рецензий')


@reviews_bp.route('/<int:review_id>/view')
@check_rights('moderate_reviews')
def view_review(review_id):
    """Страница просмотра рецензии для модерации"""
    review = Review.query.get_or_404(review_id)
    return render_template('reviews/view_review.html', review=review, title='Просмотр рецензии')


@reviews_bp.route('/<int:review_id>/approve')
@check_rights('moderate_reviews')
def approve(review_id):
    review = Review.query.get_or_404(review_id)
    approved_status = ReviewStatus.query.filter_by(name='approved').first()
    review.status_id = approved_status.id
    db.session.commit()
    flash('Рецензия одобрена', 'success')
    return redirect(url_for('reviews.moderate'))


@reviews_bp.route('/<int:review_id>/reject')
@check_rights('moderate_reviews')
def reject(review_id):
    review = Review.query.get_or_404(review_id)
    rejected_status = ReviewStatus.query.filter_by(name='rejected').first()
    review.status_id = rejected_status.id
    db.session.commit()
    flash('Рецензия отклонена', 'warning')
    return redirect(url_for('reviews.moderate'))