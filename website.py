# Базовый код всего сайта
# Импортируем flask для работы сайта и взаимодействия с сетью
from flask import Flask, render_template, redirect, request, abort
# Добавляем flask_login для работы с пользователями и авторизацией
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# импортируем datetime для сохранения картинок с уникальным именем
import datetime
# Добавляем random для генерирования случайного аватара пользователя, если он его не выберет
import random
# Импортируем os для проверки и удаления файлов
import os
# Импортируем дополнительные классы
from data import db_session
from data.posts import Posts
from data.users import User
from data.comments import Comments
# Импортируем дополнительные формы
from forms.posts import PostsForm
from forms.settings import SettingsForm
from forms.register import RegisterForm
from forms.login_form import LoginForm
from forms.comments import CommentsForm

# Создаём приложение сайта и присваиваем ему секретный ключ
app = Flask(__name__)
app.config['SECRET_KEY'] = 'denchic205_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


# Функция загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Функция входа на сайт
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Используется шаблон входа их папки шаблонов
    # При входе используется форма входа, импортированная из отдельного файла
    if not current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            # Проверка на существование пользователя и правильность пароля
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                # При успешном входе пользователя перебрасывает на главную, а при неверном логине
                # или пароле сайт об этом сообщает
                return redirect("/")
            return render_template('login.html',
                                   message="Incorrect login or password",
                                   form=form)
        return render_template('login.html', deletion=False, title='Authorisation', form=form)
    else:
        abort(404)


@app.route('/register', methods=['GET', 'POST'])
# Функция регистрации на сайте
def register():
    # Только для новых пользователей, иначе - ошибка 404
    if not current_user.is_authenticated:
        # Используется форма регистрации
        form = RegisterForm()
        # Если форма заполнена...
        if form.validate_on_submit():
            # Несовмещение паролей обрабатывается
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Registration',
                                       form=form,
                                       message="Passwords don't match")
            # Создаётся сессия в базе данных, обрабатывается возможность того, что пользователь уже существует
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Registration',
                                       form=form,
                                       message="This user is already exists")
            # Вызывается функция генерации случайного аватара, если он не был загружен
            if not form.avatar.data:
                avatar_name = avatar_function('')
            else:
                # Если аватар был указан, он загружается в папку и указвается пользователю в базу данных
                avatar = form.avatar.data
                # Обрабатывается возможность того, что загруженный файл не является картинкой
                if avatar.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                    return render_template('register.html', title='Registration',
                                           form=form,
                                           message="This file is not an image")
                # Имя аватара имеет вид Avatar {email пользователя} {текущая дата}
                avatar_name = 'Avatar ' + form.email.data + ' ' + str(datetime.datetime.now()).replace(":", "-") + \
                              '.' + avatar.filename.split('.')[-1]
                # Аватар сохраняется в папку static/img/Avatars/{Имя аватара}
                avatar.save("static/img/Avatars/" + avatar_name)
            # Проверка на фамилию, имя и возраст
            # Длина фамилии - не больше 20, имени - не более 15
            if len(form.surname.data) >= 20:
                return render_template('register.html', title='Registration',
                                       form=form,
                                       message="Your surname is so big, please, enter up to 20 characters")
            if len(form.name.data) >= 15:
                return render_template('register.html', title='Registration',
                                       form=form,
                                       message="Your name is so big, please, enter up to 15 characters")
            # Возраст - не менее 12 и не более 200
            if not form.age.data.isnumeric() or int(form.age.data) > 200:
                return render_template('register.html', title='Registration',
                                       form=form,
                                       message="Please, enter your correct age")
            if int(form.age.data) < 12:
                return render_template('register.html', title='Registration',
                                       form=form,
                                       message="We are sorry, this website is only for 12+ users")
            # Если пользователь успешно зарегестрировался, добавляем его в базу, имя и фамилию пишем с большой буквы,
            # имя аватара пользователя также добавляется в базу.
            user = User(
                surname=form.surname.data.strip()[0].upper() + form.surname.data.strip()[1:],
                name=form.name.data.strip()[0].upper() + form.name.data.strip()[1:],
                age=form.age.data.strip(),
                role=form.role.data.strip(),
                email=form.email.data.strip(),
                avatar=avatar_name,
            )
            # Пароль перед сохранением проверяется на надёжность и длину
            if check_user_password(form.password.data) != True:
                return render_template('register.html', title='Registration',
                                       form=form,
                                       message=check_user_password(form.password.data))
            user.set_password(form.password.data.strip())
            db_sess.add(user)
            # Сохраняем данные в базе и выводим пользователя из системы для дальнейшего входа
            db_sess.commit()
            logout_user()
            return redirect('/login')
        return render_template('register.html', title='Registration', form=form)
    else:
        abort(404)


@app.route("/")
def index():
    # Главная страница, которая показывает записи, или сообщает, что они все - приватные
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).all()
    count = 0
    all_private = False
    for post in posts:
        if post.is_private and post.user != current_user:
            count += 1
    if len(posts) == count:
        all_private = True
    return render_template("index.html", posts=posts, all_private=all_private, title='Denchic205 main')


@app.route('/Denchic205')
def Denchic205():
    # Страница "О сайте"
    return render_template('Denchic205.html')


@app.route('/settings/<int:id>', methods=['GET', 'POST'])
@login_required
def settings(id):
    # Насройки, для их просмотра необходимо быть зарегестрированным
    form = SettingsForm()
    # При отикрытии страницы, сначала в неё загружаются данные,
    # введённые при регистрации, а затем уже их меняет пользователь
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user and current_user == user:
            form.email.data = current_user.email
            form.surname.data = current_user.surname
            form.name.data = current_user.name
            form.age.data = current_user.age
            form.role.data = current_user.role
        else:
            abort(404)
    if form.validate_on_submit():
        # Все параметры пользователя меняются в зависимости от введённых в соответствующие поля данных
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user:
            if form.avatar.data:
                avatar = form.avatar.data
                # Все проверки повторяются из регистрации
                if avatar.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                    return render_template('settings.html', title='Settings',
                                           form=form,
                                           message="This file is not an image")
                avatar_name = 'Avatar ' + form.email.data + ' ' + str(datetime.datetime.now()).replace(
                    ":", "-") + '.' + avatar.filename.split('.')[-1]
                if avatar_function(user.avatar) and os.path.isfile('static/img/Avatars/' + user.avatar):
                    # Проверяем, был ли предыдущий аватар системным, и если нет - удаляем его из хранилища
                    os.remove('static/img/Avatars/' + user.avatar)
                avatar.save("static/img/Avatars/" + avatar_name)
            else:
                avatar_name = current_user.avatar
            if form.old_password.data and form.new_password.data:
                # Проверяется старый пароль
                if not user.check_password(form.old_password.data.strip()):
                    return render_template('settings.html', title='Settings',
                                           form=form,
                                           message="Wrong password")
                # Проверяется, совпадают ли пароли
                elif form.old_password.data.strip() == form.new_password.data.strip():
                    return render_template('settings.html', title='Settings',
                                           form=form,
                                           message="These passwords are same")
                else:
                    # Если ошибок нет, проверяем надёжность пароля и сохраняем его пользователю
                    if check_user_password(form.new_password.data) != True:
                        return render_template('settings.html', title='Settings',
                                               form=form,
                                               message=check_user_password(form.new_password.data))
                    user.set_password(form.new_password.data.strip())
            # Необычные проверки на пароли, пользователю необходимо заполнить поля, иначе - ошибка
            elif form.new_password.data and not form.old_password.data:
                return render_template('settings.html', title='Settings',
                                       form=form,
                                       message="Please, enter the previous password to continue")
            # Далее - снова проверки на данные
            if len(form.surname.data) >= 20:
                return render_template('settings.html', title='Settings',
                                       form=form,
                                       message="Your surname is so big, please, enter up to 20 characters")
            if len(form.name.data) >= 15:
                return render_template('settings.html', title='Settings',
                                       form=form,
                                       message="Your name is so big, please, enter up to 15 characters")
            user.surname = form.surname.data.strip()[0].upper() + form.surname.data.strip()[1:]
            user.name = form.name.data.strip()[0].upper() + form.name.data.strip()[1:]
            if not form.age.data.isnumeric() or int(form.age.data) > 200:
                return render_template('settings.html', title='Settings',
                                       form=form,
                                       message="Please, enter your correct age")
            if int(form.age.data) < 12:
                return render_template('settings.html', title='Settings',
                                       form=form,
                                       message="We are sorry, this website is only for 12+ users")
            # Как и при регистрации, все данные сохраняются
            print('gor')
            user.age = form.age.data.strip()
            user.role = form.role.data
            user.avatar = avatar_name
            db_sess.merge(user)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('settings.html', title='Settings', form=form)


@app.route('/logout')
@login_required
# Фунция, отключающая пользователя от сайта, выход из аккаунта
def logout():
    logout_user()
    return redirect("/")


@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    # Функция удаления пользователя, его постов и комментариев
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    # Если такой пользователь существует, и этот пользователь и вызвал эту функцию...
    if user and user == current_user:
        form = LoginForm()
        if form.validate_on_submit():
            # Проверяем данные пользователя для подтверждения удаления
            if user and user.check_password(form.password.data) and (
                    user.email == form.email.data):
                # Удаляем все посты и связанные изображения, а также комментарии
                for post in user.posts:
                    if os.path.isfile('static/img/Posts/' + post.image) and post.image != 'Empty.png':
                        os.remove('static/img/Posts/' + post.image)
                    for comment in post.comments:
                        db_sess.delete(comment)
                    db_sess.delete(post)
                # Удаляем все комментарии, которые оставил пользователь
                for comment in user.comments:
                    db_sess.delete(comment)
                # Удаляем аватар, если он не системный
                if avatar_function(user.avatar) and os.path.isfile('static/img/Avatars/' + user.avatar):
                    os.remove('static/img/Avatars/' + user.avatar)
                # Наконец, удаляем самого пользователя
                db_sess.delete(user)
                db_sess.commit()
                return redirect("/")
            return render_template('login.html',
                                   title='Log in to delete your account',
                                   deletion=True,
                                   message="Incorrect login or password",
                                   form=form)
        return render_template('login.html', title='Log in to delete your account', deletion=True, form=form)
    else:
        # Если пользователь, которого пытаются удалить - не текущий, ошибка 404
        abort(404)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
# Функция добавления поста
def add_post():
    # Пост может быть добавлен только администратором
    if current_user.role == 'Admin':
        form = PostsForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            post = Posts()
            post.type = form.type.data
            # Заголовок поста может включать в себя не более 50 символов
            if len(form.title.data) > 50:
                return render_template('addPost.html', title='Adding a post',
                                       form=form,
                                       message="This title is too big, please, enter up to 50 characters")
            post.title = form.title.data
            # Описание поста может включать в себя не более 300 символов
            if len(form.content.data) > 300:
                return render_template('addPost.html', title='Adding a post',
                                       form=form,
                                       message="This content is too big, please, enter up to 300 characters")
            post.content = form.content.data
            # Как это уже было с аватарами, изображение при его наличии сохраняется в папку
            # Если изображение не было загружено - оставляем изображение по умолчанию
            # Путь изображения: static/img/Posts/{Имя картинки поста}
            # Имя картинки имеет вид Post {текущая дата} {id текущего пользователя}
            # Картинка обрабатывается также, как и аватар, имеет аналогичные проверки на подлинность
            if not form.image.data:
                post.image = 'Empty.png'
            else:
                image = form.image.data
                if image.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                    return render_template('addPost.html', title='Adding a post',
                                           form=form,
                                           message="This file is not an image")
                filename = 'Post ' + str(datetime.datetime.now()).replace(":", "-") + f' {current_user.id}' + '.' + \
                           image.filename.split('.')[-1]
                image.save("static/img/Posts/" + filename)
                post.image = filename
            post.is_private = form.is_private.data
            current_user.posts.append(post)
            # Заполняем все поля и сохраняем пост в базу данных
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template('addPost.html', title='Adding a post',
                               form=form)
    else:
        abort(404)


@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
# Функция редактирования поста, выполнена как и добавление, а функционал - как настройки
def edit_post(id):
    form = PostsForm()
    # Заполняем поля формы, исходя из данных из базы
    if request.method == "GET":
        db_sess = db_session.create_session()
        post = db_sess.query(Posts).filter(Posts.id == id).first()
        if post and post.user == current_user:
            form.type.data = post.type
            form.title.data = post.title
            form.content.data = post.content
            form.is_private.data = post.is_private
        else:
            abort(404)
    # Затем, проверяем форму и изменяем пост
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Posts).filter(Posts.id == id).first()
        if post and post.user == current_user:
            post.type = form.type.data
            # Заголовок всё так же не более 50 символов, а описание - не более 300
            if len(form.title.data) > 50:
                return render_template('addPost.html', title='Editing a post',
                                       form=form,
                                       message="This title is too big, please, enter up to 50 characters")
            post.title = form.title.data
            if len(form.content.data) > 300:
                return render_template('addPost.html', title='Editing a post',
                                       form=form,
                                       message="This content is too big, please, enter up to 300 characters")
            post.content = form.content.data
            # Снова идёт проверка и загрузка изображения
            if form.image.data:
                image = form.image.data
                if image.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                    return render_template('addPost.html', title='Editing a post',
                                           form=form,
                                           message="This file is not an image")
                filename = 'Post ' + str(datetime.datetime.now()).replace(":", "-") + f' {current_user.id}' + '.' + \
                           image.filename.split('.')[-1]
                image.save("static/img/Posts/" + filename)
                # Изображение проверяется на нахождение в папке и на то, является ли оно изображением по умолчанию
                # Если нет, стираем его из хранилища
                if os.path.isfile('static/img/Posts/' + post.image) and post.image != 'Empty.png':
                    os.remove('static/img/Posts/' + post.image)
                post.image = filename
            post.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('addPost.html',
                           title='Editing a post',
                           form=form)


@app.route('/delete_post/<int:id>', methods=['GET', 'POST'])
@login_required
# Функция удаления поста
def delete_post(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id).first()
    if post and current_user == post.user:
        # Если пользователь в праве удалить этот пост и этот пост существует...
        # Узображение поста стирается из папки
        if os.path.isfile('static/img/Posts/' + post.image) and post.image != 'Empty.png':
            os.remove('static/img/Posts/' + post.image)
        # Все комментарии к изображению также удаляются
        for comment in post.comments:
            db_sess.delete(comment)
        # Наконец, удаляется сам пост
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/add_comment/<int:id>', methods=['GET', 'POST'])
@login_required
# Функция добавления комментария (его нельзя редактировать)
def add_comment(id):
    form = CommentsForm()
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id).first()
    # Если комментарий пэтаются оставить под чужим приватным постом или его пытается оставить пользователь
    # с ролью "Наблюдатель" - ошибка 404
    if post and (not post.is_private or (
            post.is_private and post.user == current_user)) and current_user.role != "Spectator":
        if form.validate_on_submit():
            comment = Comments()
            # Содержание комментария - не более 200 символов
            if len(form.text.data) > 200:
                return render_template('Comment.html', title='Adding a comment',
                                       form=form, post=post,
                                       message="This comment is too big, please, enter up to 200 characters")
            comment.text = form.text.data
            comment.post_id = id
            # Добавляем комментарий к пользователю и к посту
            current_user.comments.append(comment)
            db_sess.merge(current_user)
            db_sess.merge(db_sess.query(Posts).filter(Posts.id == id).first())
            db_sess.commit()
            # Пересылаем пользователя на страницу поста, под которым он оставил комментарий
            return redirect(f'/post/{id}')
        return render_template('Comment.html', title='Adding a comment',
                               form=form, post=post)
    else:
        abort(404)


@app.route('/delete_comment/<int:id>', methods=['GET', 'POST'])
@login_required
# Функция удаления комментария
def delete_comment(id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comments).filter(Comments.id == id).first()
    post_id = comment.post_id
    if comment and current_user == comment.user:
        # Если этот комментарий оставил не данный пользователь - ошибка 404, иначе удаляем комеентарий
        db_sess.delete(comment)
        db_sess.commit()
    else:
        abort(404)
    if post:
        # Если пост с комментарием существует - пересылаем пользователя на него, иначе - на главную
        return redirect(f'/post/{post_id}')
    else:
        return redirect('/')


@app.route('/post/<int:id>')
@login_required
def post(id):
    # Страница поста, указанного по id
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id).first()
    post_comments = db_sess.query(Comments).filter(Comments.post_id == id).all()
    # Пересылаем в шаблон данные поста и все комментарии для их отображения
    if post and (not post.is_private or (post.is_private and current_user == post.user)):
        return render_template('Post.html',
                               title=f'Post {post.id}', post=post, post_comments=post_comments)
    else:
        abort(404)


def check_user_password(password):
    # Функция проверки пароля
    # Длина пароля - не менее 6 символов
    if len(password.strip()) < 6:
        return 'Your password must include 6 or more characters'
    # Проверяем пароль на простоту - наличие 123, abc в пароле и сам пароль, который не может быть 'password'
    if password.strip() == 'password' or '123' in password or 'abc' in password:
        return 'Your password is so simple'
    # Также, в пароле не может быть пробелов
    if ' ' in password:
        return "Your password mustn't include any spaces"
    return True


def avatar_function(input):
    # Функция, которая при отсутствии аргумента возвращает имя аватара пользователя случайного цвета
    # При наличии аргумента функция возвращает, является ли этот аватар пользовательским
    # False, значит аватар - системный
    avatars = ['Avatar_red.png', 'Avatar_orange.png', 'Avatar_yellow.png', 'Avatar_lime.png',
               'Avatar_green.png', 'Avatar_blue.png', 'Avatar_dark-blue.png',
               'Avatar_purple.png', 'Avatar_pink.png', 'Avatar_grey.png', 'Avatar_black.png']
    if input != '':
        if input in avatars:
            return False
        else:
            return True
    else:
        return random.choice(avatars)


def main():
    # Подключаем базу к приложению и запускаем его на сервере
    db_session.global_init("db/users.db")
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
