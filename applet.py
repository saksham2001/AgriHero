import os
import secrets
from flask import Flask, render_template, url_for, flash, redirect, request
from markupsafe import escape
from dbms import DB, User
from forms import RegistrationForm, LoginForm, AccountForm, PostForm, ResetForm1, ResetForm2
from flask_login import login_user, LoginManager, logout_user, current_user, login_required
from grapher import create_plot, create_heatmap

db = DB('site.db')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'saksham2001'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(username):
    user = User(username)
    return user


@app.route('/home')
@login_required
def home():
    bar = create_plot()
    heatmap = create_heatmap()
    return render_template('home.html', sensors=db.get_sensor(), title='Home', plot=bar, heatmap=heatmap)


@app.route('/')
@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/news')
def news_page():
    return render_template('news.html', sensors=db.get_sensor())

@app.route('/buyandsell')
@login_required
def buyandsell_page():
    heatmap = create_heatmap()
    return render_template('buyandsell.html', heatmap=heatmap)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.add_user(form.username.data, form.email.data, form.password.data):
            flash(f'Account Created for {form.username.data}, You will now be able to login!', category='success')
            return redirect(url_for('login'))
        else:
            flash('Sorry, Account already exists!', category='danger')
            return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        if db.check_login(form.username.data, form.password.data):
            user = User(form.username.data)
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    img = url_for('static', filename='profile_pics/' + current_user.image)
    form = AccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            random_hex = secrets.token_hex(8)
            _, p_ext = os.path.splitext(form.picture.data.filename)
            p_fn = random_hex + p_ext
            picture_path = os.path.join(app.root_path, 'static/profile_pics', p_fn)
            form.picture.data.save(picture_path)
            db.update_picture(p_fn, current_user.username)
            current_user.image = p_fn
            flash('Picture Successfully Updated', 'success')
            return redirect(url_for('account'))
    return render_template('account.html', title='Account', form=form, image_file=img)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        flash('Your Post has been Posted!', 'success')
        db.add_sensor(current_user.user_id, form.title.data, form.content.data)
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


@app.route('/user/<username>')
@login_required
def user_page(username):
    sensors = db.get_sensor(username=username)
    if len(sensors) == 0:
        flash('User Does not Exists!', 'danger')
        return redirect(url_for('home'))
    else:
        return render_template('user.html', sensors=sensors, title='Home', username=escape(username))


# @app.route('/reset-password-username')
# def reset_password_username():
#     form = ResetForm1()
#     if form.validate_on_submit():
#         user = User(form.username.data)
#         token = user.reset_pass()
#         send_email(token)
#         flash('An email has been sent with instructions to reset your password.', 'info')
#         return redirect(url_for('login'))
#
#     return render_template('reset_password_username.html')
#
#
# @app.route('/reset-password/<token>')
# def reset_password(token):
#     user_id =
#     form = ResetForm2()



if __name__ == '__main__':
    app.run(debug=True)
