from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import datetime
from data import db_session
from data.posts import Posts
from forms.posts import PostsForm
from data.users import User
from forms.user import RegisterForm
from data.login_form import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
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
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", posts=posts, names=names, title='Denchic205 main')


@app.route('/Denchic205')
def Denchic205():
    return render_template('Denchic205.html')


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

        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            address=form.address.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        print('User added')
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addPost', methods=['GET', 'POST'])
def addPost():
    form = PostsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = Posts()
        if len(form.title.data) > 50:
            return render_template('addPost.html', title='Добавление записи',
                                   form=form,
                                   message="Слишком большой заголовок записи")
        posts.title = form.title.data
        posts.content = form.content.data
        if not form.image.data:
            posts.image = 'Empty.jpg'
        else:
            image = form.image.data
            print(image)
            if image.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                return render_template('addPost.html', title='Добавление записи',
                                       form=form,
                                       message="Файл не является изображением")
            filename = 'post ' + str(datetime.datetime.now()).split('.')[0].replace(":", "-") + '.' + \
                           image.filename.split('.')[-1]
            image.save("static/img/" + filename)
            posts.image = filename
        posts.is_private = form.is_private.data
        print(form.is_private.data)
        current_user.posts.append(posts)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('addPost.html', title='Добавление записи',
                           form=form)


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id).first()
        if posts:
            form.title.data = posts.title
            form.content.data = posts.content
            form.is_private.data = posts.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id).first()
        if posts:
            if len(form.title.data) > 50:
                return render_template('addPost.html', title='Редактирование записи',
                                       form=form,
                                       message="Слишком большой заголовок записи")
            posts.title = form.title.data
            posts.content = form.content.data
            if form.image.data:
                image = form.image.data
                if image.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                    return render_template('addPost.html', title='Добавление записи',
                                           form=form,
                                           message="Файл не является изображением")
                filename = 'post ' + str(datetime.datetime.now()).split('.')[0].replace(":", "-") + '.' + \
                           image.filename.split('.')[-1]
                image.save("static/img/" + filename)
                posts.image = filename
            posts.is_private = form.is_private.data
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
    if post:
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
