from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import datetime
import random
import os
from data import db_session
from data.posts import Posts
from data.users import User
from data.comments import Comments
from forms.posts import PostsForm
from forms.settings import SettingsForm
from forms.register import RegisterForm
from forms.login_form import LoginForm
from forms.comments import CommentsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'denchic205_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', deletion=False, form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_session.global_init("db/users.db")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        print('Adding user...')
        if not form.avatar.data:
            avatar_name = avatar_function('')
        else:
            avatar = form.avatar.data
            if avatar.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Файл не является изображением")
            avatar_name = 'Avatar_' + form.email.data + '_' + str(datetime.datetime.now()).replace(":", "-") + \
                          '.' + avatar.filename.split('.')[-1]
            avatar.save("static/img/Avatars/" + avatar_name)
        if not form.age.data.isnumeric() or int(form.age.data) > 200:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пожалуйста, введите корректный возраст")
        if int(form.age.data) < 12:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Простите, на сайте действует возрастное ограничение 12+")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            address=form.address.data,
            email=form.email.data,
            avatar=avatar_name,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        print('User added')
        logout_user()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    count = 0
    all_private = False
    for post in posts:
        if post.is_private and post.user != current_user:
            count += 1
    if len(posts) == count:
        all_private = True
    return render_template("index.html", posts=posts, names=names, all_private=all_private, title='Denchic205 main')


@app.route('/Denchic205')
def Denchic205():
    return render_template('Denchic205.html')


@app.route('/settings/<int:id>', methods=['GET', 'POST'])
@login_required
def settings(id):
    form = SettingsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user and current_user == user:
            form.email.data = current_user.email
            form.surname.data = current_user.surname
            form.name.data = current_user.name
            form.age.data = current_user.age
            form.address.data = current_user.address
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user:
            if form.avatar.data:
                avatar = form.avatar.data
                if avatar.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                    return render_template('settings.html', title='Настройки',
                                           form=form,
                                           message="Файл не является изображением")
                avatar_name = 'Avatar_' + form.email.data + '_' + str(datetime.datetime.now()).replace(
                    ":", "-") + '.' + avatar.filename.split('.')[-1]
                if avatar_function(user.avatar) and os.path.isfile('static/img/Avatars/' + user.avatar):
                    os.remove('static/img/Avatars/' + user.avatar)
                avatar.save("static/img/Avatars/" + avatar_name)
            else:
                avatar_name = current_user.avatar
            if form.old_password.data and form.new_password.data:
                if not user.check_password(form.old_password.data):
                    return render_template('settings.html', title='Настройки',
                                           form=form,
                                           message="Неправильный пароль")
                elif form.old_password.data == form.new_password.data:
                    return render_template('settings.html', title='Настройки',
                                           form=form,
                                           message="Пароли совпадают")
                else:
                    user.set_password(form.new_password.data)
            elif form.new_password.data and not form.old_password.data:
                return render_template('settings.html', title='Настройки',
                                       form=form,
                                       message="Введите предыдущий пароль, чтобы продолжить")
            user.surname = form.surname.data
            user.name = form.name.data
            if not form.age.data.isnumeric() or int(form.age.data) > 200:
                return render_template('settings.html', title='Настройки',
                                       form=form,
                                       message="Пожалуйста, введите корректный возраст")
            if int(form.age.data) < 12:
                return render_template('settings.html', title='Настройки',
                                       form=form,
                                       message="Простите, на сайте действует возрастное ограничение 12+")
            user.age = form.age.data
            user.address = form.address.data
            user.avatar = avatar_name
            db_sess.merge(user)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('settings.html', title='Настройки', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if user and user == current_user:
        form = LoginForm()
        if form.validate_on_submit():
            if user and user.check_password(form.password.data) and user.email == current_user.email:
                for post in user.posts:
                    if os.path.isfile('static/img/Posts/' + post.image) and post.image != 'Empty.png':
                        os.remove('static/img/Posts/' + post.image)
                    for comment in post.comments:
                        db_sess.delete(comment)
                    db_sess.delete(post)
                print('All posts deleted')
                for comment in user.comments:
                    db_sess.delete(comment)
                print('All comments deleted')
                if avatar_function(user.avatar) and os.path.isfile('static/img/Avatars/' + user.avatar):
                    os.remove('static/img/Avatars/' + user.avatar)
                db_sess.delete(user)
                db_sess.commit()
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Удаление пользователя', deletion=True, form=form)
    else:
        abort(404)


@app.route('/addPost', methods=['GET', 'POST'])
@login_required
def addPost():
    form = PostsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Posts()
        post.type = form.type.data
        if len(form.title.data) > 50:
            return render_template('addPost.html', title='Добавление записи',
                                   form=form,
                                   message="Слишком большой заголовок записи")
        post.title = form.title.data
        if len(form.content.data) > 300:
            return render_template('addPost.html', title='Добавление записи',
                                   form=form,
                                   message="Слишком большое описание")
        post.content = form.content.data
        if not form.image.data:
            post.image = 'Empty.png'
        else:
            image = form.image.data
            if image.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                return render_template('addPost.html', title='Добавление записи',
                                       form=form,
                                       message="Файл не является изображением")
            filename = 'post ' + str(datetime.datetime.now()).replace(":", "-") + '.' + \
                       image.filename.split('.')[-1]
            image.save("static/img/Posts/" + filename)
            post.image = filename
        post.is_private = form.is_private.data
        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('addPost.html', title='Добавление записи',
                           form=form)


@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostsForm()
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
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Posts).filter(Posts.id == id).first()
        if post and post.user == current_user:
            post.type = form.type.data
            if len(form.title.data) > 50:
                return render_template('addPost.html', title='Редактирование записи',
                                       form=form,
                                       message="Слишком большой заголовок записи")
            post.title = form.title.data
            if len(form.content.data) > 300:
                return render_template('addPost.html', title='Добавление записи',
                                       form=form,
                                       message="Слишком большое описание")
            post.content = form.content.data
            if form.image.data:
                image = form.image.data
                if image.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                    return render_template('addPost.html', title='Добавление записи',
                                           form=form,
                                           message="Файл не является изображением")
                filename = 'post ' + str(datetime.datetime.now()).replace(":", "-") + '.' + \
                           image.filename.split('.')[-1]
                image.save("static/img/posts/" + filename)
                if os.path.isfile('static/img/Posts/' + post.image) and post.image != 'Empty.png':
                    os.remove('static/img/Posts/' + post.image)
                post.image = filename
            post.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('addPost.html',
                           title='Редактирование записи',
                           form=form)


@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id).first()
    if post and current_user == post.user:
        if os.path.isfile('static/img/Posts/' + post.image) and post.image != 'Empty.png':
            os.remove('static/img/Posts/' + post.image)
        for comment in post.comments:
            db_sess.delete(comment)
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/add_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def add_comment(id):
    form = CommentsForm()
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id).first()
    if not post.is_private or (post.is_private and post.user == current_user):
        if form.validate_on_submit():
            comment = Comments()
            if len(form.text.data) > 200:
                return render_template('Comment.html', title='Добавление комментария',
                                       form=form,
                                       message="Слишком большой комментарий, пожалуйста, введите не более 200 символов")
            comment.text = form.text.data
            comment.post_id = id
            current_user.comments.append(comment)
            db_sess.merge(current_user)
            db_sess.merge(db_sess.query(Posts).filter(Posts.id == id).first())
            db_sess.commit()
            db_sess.close()
            return redirect(f'/post/{id}')
        return render_template('Comment.html', title='Добавление комментария',
                               form=form, post=post)
    else:
        abort(404)


@app.route('/comment_delete/<int:id>', methods=['GET', 'POST'])
def comment_delete(id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comments).filter(Comments.id == id).first()
    post_id = comment.post_id
    if comment and current_user == comment.user:
        db_sess.delete(comment)
        db_sess.commit()
    else:
        abort(404)
    if post:
        return redirect(f'/post/{post_id}')


@app.route('/post/<int:id>')
@login_required
def post(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id).first()
    post_comments = db_sess.query(Comments).filter(Comments.post_id == id).all()
    if post and (not post.is_private or (post.is_private and current_user == post.user)):
        return render_template('Post.html',
                               title=f'Post {post.id}', post=post, post_comments=post_comments)
    else:
        abort(404)


def avatar_function(input):
    colors = ['red', 'orange', 'yellow', 'lime', 'green', 'blue', 'dark-blue', 'purple', 'pink', 'grey', 'black']
    if input != '':
        if input.split('_')[1].split('.')[0] in colors:
            return False
        else:
            return True
    else:
        return 'Avatar_' + random.choice(colors) + '.png'


def main():
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
