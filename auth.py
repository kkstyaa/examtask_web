from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user

def check_rights(action):
    """
    Декоратор для проверки прав пользователя.
    action: 'create_book', 'edit_book', 'delete_book', 'moderate_reviews'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Для выполнения данного действия необходимо пройти процедуру аутентификации.', 'warning')
                return redirect(url_for('login', next=request.url))

            # администратор может всё
            if current_user.is_admin():
                return f(*args, **kwargs)

            # проверки для разных действий
            if action == 'create_book':
                # только администратор может создавать книги
                flash('У вас недостаточно прав для создания книги.', 'danger')
                return redirect(url_for('books.index'))

            elif action == 'delete_book':
                # только администратор может удалять книги
                flash('У вас недостаточно прав для удаления книги.', 'danger')
                return redirect(url_for('books.index'))

            elif action == 'edit_book':
                if current_user.is_moderator():
                    return f(*args, **kwargs)
                flash('У вас недостаточно прав для редактирования книги.', 'danger')
                return redirect(url_for('books.index'))

            elif action == 'moderate_reviews':
                if current_user.is_moderator():
                    return f(*args, **kwargs)
                flash('У вас недостаточно прав для модерации рецензий.', 'danger')
                return redirect(url_for('books.index'))

            flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
            return redirect(url_for('books.index'))

        return decorated_function
    return decorator