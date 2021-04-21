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
                               message="Incorrect login or password",
                               form=form)
    return render_template('login.html', title='Authorisation', deletion=False, form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Passwords don't match")
        db_session.global_init("db/users.db")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="This user is already exists")
        if not form.avatar.data:
            avatar_name = avatar_function('')
        else:
            avatar = form.avatar.data
            if avatar.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                return render_template('register.html', title='Registration',
                                       form=form,
                                       message="This file is not an image")
            avatar_name = 'Avatar_' + form.email.data + '_' + str(datetime.datetime.now()).replace(":", "-") + \
                          '.' + avatar.filename.split('.')[-1]
            avatar.save("static/img/Avatars/" + avatar_name)
        if len(form.surname.data) >= 20:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Your surname is so big, please, enter up to 20 characters")
        if len(form.name.data) >= 15:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Your name is so big, please, enter up to 15 characters")
        if not form.age.data.isnumeric() or int(form.age.data) > 200:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Please, enter your correct age")
        if int(form.age.data) < 12:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="We are sorry, this website is only for 12+ users")
        user = User(
            surname=form.surname.data.strip()[0].upper() + form.surname.data.strip()[1:],
            name=form.name.data.strip()[0].upper() + form.name.data.strip()[1:],
            age=form.age.data.strip(),
            role=form.role.data.strip(),
            address=form.address.data.strip(),
            email=form.email.data.strip(),
            avatar=avatar_name,
        )
        if check_user_password(form.password.data) != True:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message=check_user_password(form.password.data))
        user.set_password(form.password.data.strip())
        db_sess.add(user)
        db_sess.commit()
        logout_user()
        return redirect('/login')
    return render_template('register.html', title='Registration', form=form)


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
            form.role.data = current_user.role
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
                    return render_template('settings.html', title='Settings',
                                           form=form,
                                           message="This file is not an image")
                avatar_name = 'Avatar_' + form.email.data + '_' + str(datetime.datetime.now()).replace(
                    ":", "-") + '.' + avatar.filename.split('.')[-1]
                if avatar_function(user.avatar) and os.path.isfile('static/img/Avatars/' + user.avatar):
                    os.remove('static/img/Avatars/' + user.avatar)
                avatar.save("static/img/Avatars/" + avatar_name)
            else:
                avatar_name = current_user.avatar
            if form.old_password.data and form.new_password.data:
                if not user.check_password(form.old_password.data.strip()):
                    return render_template('settings.html', title='Settings',
                                           form=form,
                                           message="Wrong password")
                elif form.old_password.data.strip() == form.new_password.data.strip():
                    return render_template('settings.html', title='Settings',
                                           form=form,
                                           message="These passwords are same")
                else:
                    user.set_password(form.new_password.data.strip())
            elif form.new_password.data and not form.old_password.data:
                return render_template('settings.html', title='Settings',
                                       form=form,
                                       message="Please, enter the previous password to continue")
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
            user.age = form.age.data.strip()
            user.role = form.role.data
            user.address = form.address.data.strip()
            user.avatar = avatar_name
            db_sess.merge(user)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('settings.html', title='Settings', form=form)


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
            if user and user.check_password(form.password.data) and (
                    user.email == form.email.data):
                for post in user.posts:
                    if os.path.isfile('static/img/Posts/' + post.image) and post.image != 'Empty.png':
                        os.remove('static/img/Posts/' + post.image)
                    for comment in post.comments:
                        db_sess.delete(comment)
                    db_sess.delete(post)
                for comment in user.comments:
                    db_sess.delete(comment)
                if avatar_function(user.avatar) and os.path.isfile('static/img/Avatars/' + user.avatar):
                    os.remove('static/img/Avatars/' + user.avatar)
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
        abort(404)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if current_user.role == 'Admin':
        form = PostsForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            post = Posts()
            post.type = form.type.data
            if len(form.title.data) > 50:
                return render_template('addPost.html', title='Adding a post',
                                       form=form,
                                       message="This title is too big, please, enter up to 50 characters")
            post.title = form.title.data
            if len(form.content.data) > 300:
                return render_template('addPost.html', title='Adding a post',
                                       form=form,
                                       message="This content is too big, please, enter up to 300 characters")
            post.content = form.content.data
            if not form.image.data:
                post.image = 'Empty.png'
            else:
                image = form.image.data
                if image.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                    return render_template('addPost.html', title='Adding a post',
                                           form=form,
                                           message="This file is not an image")
                filename = 'post ' + str(datetime.datetime.now()).replace(":", "-") + '.' + \
                           image.filename.split('.')[-1]
                image.save("static/img/Posts/" + filename)
                post.image = filename
            post.is_private = form.is_private.data
            current_user.posts.append(post)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template('addPost.html', title='Adding a post',
                               form=form)
    else:
        abort(404)


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
                return render_template('addPost.html', title='Editing a post',
                                       form=form,
                                       message="This title is too big, please, enter up to 50 characters")
            post.title = form.title.data
            if len(form.content.data) > 300:
                return render_template('addPost.html', title='Editing a post',
                                       form=form,
                                       message="This content is too big, please, enter up to 300 characters")
            post.content = form.content.data
            if form.image.data:
                image = form.image.data
                if image.filename.split('.')[-1] not in ['png', 'jpeg', 'jpg', 'ico', 'gif', 'bmp']:
                    return render_template('addPost.html', title='Editing a post',
                                           form=form,
                                           message="This file is not an image")
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
                           title='Editing a post',
                           form=form)


@app.route('/delete_post/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
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
    if post and (not post.is_private or (
            post.is_private and post.user == current_user)) and current_user.role != "Spectator":
        if form.validate_on_submit():
            comment = Comments()
            if len(form.text.data) > 200:
                return render_template('Comment.html', title='Adding a comment',
                                       form=form, post=post,
                                       message="This comment is too big, please, enter up to 200 characters")
            comment.text = form.text.data
            comment.post_id = id
            current_user.comments.append(comment)
            db_sess.merge(current_user)
            db_sess.merge(db_sess.query(Posts).filter(Posts.id == id).first())
            db_sess.commit()
            db_sess.close()
            return redirect(f'/post/{id}')
        return render_template('Comment.html', title='Adding a comment',
                               form=form, post=post)
    else:
        abort(404)


@app.route('/delete_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
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


def check_user_password(password):
    if len(password.strip()) < 6:
        return 'Your password must include 6 or more characters'
    if password.strip() == 'password' or '123' in password or 'abc' in password:
        return 'Your password is so simple'
    if ' ' in password:
        return "Your password mustn't include any spaces"
    return True


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
