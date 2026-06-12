import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Role, User, Genre, ReviewStatus, Book, Cover, Review

def init_database():
    with app.app_context():
        print("Удаление существующих таблиц...")
        db.drop_all()
        
        print("Создание таблиц...")
        db.create_all()
        
        print("\nСоздание ролей...")
        roles_data = [
            {'name': 'admin', 'description': 'Администратор — полный доступ к системе'},
            {'name': 'moderator', 'description': 'Модератор — может редактировать книги и модерировать рецензии'},
            {'name': 'user', 'description': 'Пользователь — может оставлять рецензии'}
        ]
        
        roles = {}
        for role_data in roles_data:
            role = Role(**role_data)
            db.session.add(role)
            roles[role_data['name']] = role
            print(f"Создана роль: {role_data['name']}")
        
        db.session.commit()
        
        print("\nСоздание пользователей...")
        users_data = [
            {
                'login': 'admin',
                'password': 'Admin123!',
                'last_name': 'Кленечева',
                'first_name': 'Анастасия',
                'middle_name': 'Владимировна',
                'role': roles['admin']
            },
            {
                'login': 'moderator',
                'password': 'Moder123!',
                'last_name': 'Петрова',
                'first_name': 'Мария',
                'middle_name': 'Ивановна',
                'role': roles['moderator']
            },
            {
                'login': 'ivanov',
                'password': 'User123!',
                'last_name': 'Иванов',
                'first_name': 'Иван',
                'middle_name': 'Петрович',
                'role': roles['user']
            },
            {
                'login': 'petrova',
                'password': 'User123!',
                'last_name': 'Петрова',
                'first_name': 'Анна',
                'middle_name': 'Сергеевна',
                'role': roles['user']
            },
            {
                'login': 'sidorov',
                'password': 'User123!',
                'last_name': 'Сидоров',
                'first_name': 'Алексей',
                'middle_name': 'Дмитриевич',
                'role': roles['user']
            },
            {
                'login': 'kozlova',
                'password': 'User123!',
                'last_name': 'Козлова',
                'first_name': 'Екатерина',
                'middle_name': 'Андреевна',
                'role': roles['user']
            }
        ]
        
        for user_data in users_data:
            password = user_data.pop('password')
            role = user_data.pop('role')
            
            user = User(**user_data)
            user.set_password(password)
            user.role = role
            
            db.session.add(user)
            print(f"Создан пользователь: {user_data['login']} ({role.name})")
        
        db.session.commit()
        
        print("\nСоздание жанров...")
        genres_data = [
            'Фантастика', 'Детектив', 'Роман', 'Научная литература',
            'Приключения', 'Фэнтези', 'Триллер', 'Историческая проза', 
            'Поэзия', 'Драма', 'Классика', 'Научная фантастика', 'Киберпанк'
        ]
        
        genres = {}
        for genre_name in genres_data:
            genre = Genre(name=genre_name)
            db.session.add(genre)
            genres[genre_name] = genre
            print(f"Создан жанр: {genre_name}")
        
        db.session.commit()
        
        print("\nСоздание книг (10 штук)...")
        books_data = [
            {
                'title': 'Мастер и Маргарита',
                'description': 'Роман Михаила Булгакова, в котором переплетаются две сюжетные линии: сатанинские игры в Москве и история любви Понтия Пилата и Иешуа Га-Ноцри.',
                'year': 1967,
                'publisher': 'Художественная литература',
                'author': 'Михаил Булгаков',
                'pages': 480,
                'genres': ['Роман', 'Драма', 'Классика']
            },
            {
                'title': '1984',
                'description': 'Роман-антиутопия Джорджа Оруэлла о тоталитарном режиме и подавлении личности.',
                'year': 1949,
                'publisher': 'АСТ',
                'author': 'Джордж Оруэлл',
                'pages': 328,
                'genres': ['Фантастика', 'Драма', 'Классика']
            },
            {
                'title': 'Гарри Поттер и философский камень',
                'description': 'Первый роман о мальчике-волшебнике Гарри Поттере, который узнаёт о своих магических способностях и поступает в школу чародейства и волшебства Хогвартс.',
                'year': 1997,
                'publisher': 'Росмэн',
                'author': 'Джоан Роулинг',
                'pages': 350,
                'genres': ['Фэнтези', 'Приключения']
            },
            # НОВЫЕ КНИГИ
            {
                'title': 'Преступление и наказание',
                'description': 'Роман Фёдора Достоевского о студенте Родионе Раскольникове, который совершает убийство и сталкивается с муками совести.',
                'year': 1866,
                'publisher': 'Русский вестник',
                'author': 'Фёдор Достоевский',
                'pages': 672,
                'genres': ['Роман', 'Драма', 'Классика']
            },
            {
                'title': 'Война и мир',
                'description': 'Эпопея Льва Толстого о жизни русского общества в эпоху наполеоновских войн.',
                'year': 1869,
                'publisher': 'Русский вестник',
                'author': 'Лев Толстой',
                'pages': 1300,
                'genres': ['Роман', 'Историческая проза', 'Классика']
            },
            {
                'title': 'Автостопом по Галактике',
                'description': 'Юмористический научно-фантастический роман Дугласа Адамса о приключениях незадачливого англичанина Артура Дента.',
                'year': 1979,
                'publisher': 'Pan Books',
                'author': 'Дуглас Адамс',
                'pages': 216,
                'genres': ['Фантастика', 'Научная фантастика', 'Юмор']
            },
            {
                'title': 'Нейромант',
                'description': 'Классический киберпанк-роман Уильяма Гибсона о хакере, которого нанимают для последнего взлома.',
                'year': 1984,
                'publisher': 'Ace Books',
                'author': 'Уильям Гибсон',
                'pages': 288,
                'genres': ['Научная фантастика', 'Киберпанк']
            },
            {
                'title': 'Убить пересмешника',
                'description': 'Роман Харпер Ли о расовой несправедливости в американском юге глазами маленькой девочки.',
                'year': 1960,
                'publisher': 'J.B. Lippincott & Co.',
                'author': 'Харпер Ли',
                'pages': 336,
                'genres': ['Драма', 'Классика']
            },
            {
                'title': '451 градус по Фаренгейту',
                'description': 'Роман-антиутопия Рэя Брэдбери о мире, где книги запрещены и сжигаются.',
                'year': 1953,
                'publisher': 'Ballantine Books',
                'author': 'Рэй Брэдбери',
                'pages': 256,
                'genres': ['Научная фантастика', 'Драма']
            },
            {
                'title': 'Три товарища',
                'description': 'Роман Эриха Марии Ремарка о дружбе и любви в Германии между мировыми войнами.',
                'year': 1936,
                'publisher': 'Propyläen Verlag',
                'author': 'Эрих Мария Ремарк',
                'pages': 448,
                'genres': ['Роман', 'Драма']
            }
        ]
        
        books = []
        for book_data in books_data:
            genres_for_book = book_data.pop('genres')
            book = Book(**book_data)
            for genre_name in genres_for_book:
                if genre_name in genres:
                    book.genres.append(genres[genre_name])
            db.session.add(book)
            books.append(book)
            print(f"Создана книга: {book_data['title']}")
        
        db.session.commit()
        
        print("\nСоздание статусов рецензий...")
        statuses_data = ['pending', 'approved', 'rejected']
        status_descriptions = {
            'pending': 'На рассмотрении',
            'approved': 'Одобрена',
            'rejected': 'Отклонена'
        }
        
        review_statuses = {}
        for status_name in statuses_data:
            status = ReviewStatus(name=status_name)
            db.session.add(status)
            review_statuses[status_name] = status
            print(f"Создан статус: {status_name} — {status_descriptions[status_name]}")
        
        db.session.commit()
        
        print("\nСоздание рецензий...")
        
        # получаем пользователей
        ivanov = User.query.filter_by(login='ivanov').first()
        petrova = User.query.filter_by(login='petrova').first()
        sidorov = User.query.filter_by(login='sidorov').first()
        kozlova = User.query.filter_by(login='kozlova').first()
        
        # получаем статусы
        pending_status = ReviewStatus.query.filter_by(name='pending').first()
        approved_status = ReviewStatus.query.filter_by(name='approved').first()
        rejected_status = ReviewStatus.query.filter_by(name='rejected').first()
        
        # получаем книги
        master_margarita = Book.query.filter_by(title='Мастер и Маргарита').first()
        book_1984 = Book.query.filter_by(title='1984').first()
        harry_potter = Book.query.filter_by(title='Гарри Поттер и философский камень').first()
        crime_punishment = Book.query.filter_by(title='Преступление и наказание').first()
        war_peace = Book.query.filter_by(title='Война и мир').first()
        hitchhiker = Book.query.filter_by(title='Автостопом по Галактике').first()
        neuromancer = Book.query.filter_by(title='Нейромант').first()
        mockingbird = Book.query.filter_by(title='Убить пересмешника').first()
        fahrenheit = Book.query.filter_by(title='451 градус по Фаренгейту').first()
        comrades = Book.query.filter_by(title='Три товарища').first()
        
        reviews_data = [
            {
                'book': master_margarita,
                'user': ivanov,
                'rating': 5,
                'text': 'Гениальное произведение! Булгаков создал уникальный мир, где переплетаются реальность и мистика. Обязательно к прочтению!',
                'status': approved_status
            },
            {
                'book': master_margarita,
                'user': petrova,
                'rating': 4,
                'text': 'Очень интересно, хотя некоторые моменты сложноваты для понимания. Но в целом — шедевр.',
                'status': pending_status
            },
            {
                'book': book_1984,
                'user': ivanov,
                'rating': 5,
                'text': 'Пугающе актуальная книга. Оруэлл предвидел многое из того, что происходит в современном мире. Настоятельно рекомендую.',
                'status': approved_status
            },
            {
                'book': harry_potter,
                'user': petrova,
                'rating': 5,
                'text': 'Любимая книга с детства! Магия, дружба, приключения — всё, что нужно для отличного чтения.',
                'status': approved_status
            },
            {
                'book': crime_punishment,
                'user': ivanov,
                'rating': 5,
                'text': 'Глубокий психологический роман. Достоевский мастерски показывает внутренние метания человека. Очень тяжело, но невероятно важно к прочтению.',
                'status': approved_status
            },
            {
                'book': crime_punishment,
                'user': sidorov,
                'rating': 4,
                'text': 'Интересно, но местами слишком затянуто. Однако концовка впечатляет.',
                'status': pending_status
            },
            {
                'book': war_peace,
                'user': petrova,
                'rating': 5,
                'text': 'Монументальное произведение! Толстой создал целую вселенную. Читала несколько месяцев, но оно того стоило.',
                'status': approved_status
            },
            {
                'book': hitchhiker,
                'user': sidorov,
                'rating': 5,
                'text': 'Очень смешно! Лучшая юмористическая фантастика, которую я читал. 42 — ответ на всё!',
                'status': approved_status
            },
            {
                'book': neuromancer,
                'user': kozlova,
                'rating': 4,
                'text': 'Классика киберпанка. Стиль Гибсона уникален, но сюжет местами сложноват для восприятия.',
                'status': approved_status
            },
            {
                'book': mockingbird,
                'user': kozlova,
                'rating': 5,
                'text': 'Трогательная и мудрая книга о справедливости, доброте и взрослении. Аттикус Финч — один из лучших литературных героев.',
                'status': approved_status
            },
            {
                'book': fahrenheit,
                'user': ivanov,
                'rating': 5,
                'text': 'Брэдбери гениален! Эта антиутопия пугает своей пророческой силой. Книги действительно важны.',
                'status': pending_status
            },
            {
                'book': comrades,
                'user': petrova,
                'rating': 4,
                'text': 'Ремарк как всегда прекрасен. Грустная, но красивая история о дружбе и любви.',
                'status': approved_status
            },
            {
                'book': comrades,
                'user': sidorov,
                'rating': 5,
                'text': 'Одна из лучших книг о настоящей мужской дружбе. Прочитал на одном дыхании.',
                'status': approved_status
            }
        ]
        
        for review_data in reviews_data:
            review = Review(
                book=review_data['book'],
                user=review_data['user'],
                rating=review_data['rating'],
                text=review_data['text'],
                status=review_data['status']
            )
            db.session.add(review)
            print(f"Создана рецензия: {review_data['user'].login} → {review_data['book'].title} (оценка: {review_data['rating']}, статус: {review_data['status'].name})")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("БАЗА ДАННЫХ УСПЕШНО ИНИЦИАЛИЗИРОВАНА!")
        print("="*60)
        
        print("\nСтатистика:")
        print(f"  • Ролей: {Role.query.count()}")
        print(f"  • Пользователей: {User.query.count()}")
        print(f"  • Жанров: {Genre.query.count()}")
        print(f"  • Книг: {Book.query.count()}")
        print(f"  • Рецензий: {Review.query.count()}")
        
        print("\nУчётные записи для входа:")
        print("-" * 40)
        print(f"{'Логин':<12} | {'Пароль':<12} | {'Роль':<12}")
        print("-" * 40)
        print(f"{'admin':<12} | {'Admin123!':<12} | {'Администратор':<12}")
        print(f"{'moderator':<12} | {'Moder123!':<12} | {'Модератор':<12}")
        print(f"{'ivanov':<12} | {'User123!':<12} | {'Пользователь':<12}")
        print(f"{'petrova':<12} | {'User123!':<12} | {'Пользователь':<12}")
        print(f"{'sidorov':<12} | {'User123!':<12} | {'Пользователь':<12}")
        print(f"{'kozlova':<12} | {'User123!':<12} | {'Пользователь':<12}")
        print("-" * 40)

if __name__ == '__main__':
    init_database()