#import datetime
import os
import secrets

from werkzeug.security import check_password_hash, generate_password_hash
import base64
from flask import request, redirect, render_template, session, flash, Response, current_app
#from Fag_gag import login_manager
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user
#from Fag_gag import Users, app, db
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import DateTime
from datetime import datetime, date
#import flask_login

#from app.views import login_manager
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'secret'
#login_manager = flask_login.LoginManager(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


class Users(db.Model, UserMixin):
    # __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    nick = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(30), nullable=False)


    #post = db.relationship('Post')
class User_info(db.Model):
    id = db.column(db.Integer(), primary_key=True)
    vk_id = db.Column(db.String(130))
    name = db.Column(db.String(120), nullable=False)
    hostel = db.Column(db.String(120))
    mobile_number = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(120), default='image.jpg')
    image2 = db.Column(db.String(120), default='image2.jpg')
    image3 = db.Column(db.String(120), default='image3.jpg')
    image4 = db.Column(db.String(120), default='image4.jpg')
    image5 = db.Column(db.String(120), default='image5.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('Users', backref=db.backref('author', lazy=True))
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean())
    hostel = db.Column(db.String(120), nullable=False)
    vk = db.relationship('Users', backref=db.backref('vk', lazy=True))

    #photos = db.relationship('Photo')


#login_manager.init_app(app)

def save_img(photo):

    hash_photo = secrets.token_urlsafe(10)
    _, file_extention = os.path.splitext(photo.filename)
    photo_name = hash_photo + file_extention
    file_path = os.path.join(current_app.root_path, 'static/img', photo_name)
    photo.save(file_path)
    return photo_name


@app.route('/main')
@app.route('/')
def main_page():
    ctg = request.args.get('ctg')
    if ctg:
        posts = Post.query.filter(Post.category.contains(ctg), Post.active == True)
    else:
        posts = Post.query.order_by(Post.id.desc(), Post.active == True).all()
    return render_template('main.html', posts=posts)



@app.route('/user', methods=['POST', 'GET'])
def user():
    if request.method == 'POST':
        nick = request.form['nick']
        password = request.form['password']
        hash_pwd = generate_password_hash(password)
        users = Users(nick=nick, password=hash_pwd)

        try:
            db.session.add(users)
            db.session.commit()
            return redirect('/login')
        except:
            return 'ERROR'
    else:
        return render_template('user.html')


@app.route('/user-info')
def add_info():
    if request.method == 'POST':
        name = request.form['name']
        vk_id = request.form['vk_id']
        hostel = request.form['hostel']
        mobile_number = request.form['mobile_number']
        info = Users(name=name, vk_id=vk_id, hostel=hostel, mobile_number=mobile_number)
        try:
            db.session.add(info)
            db.session.commit()
            return redirect('/login')
        except:
            return 'ERROR'
    else:
        return render_template('user-info.html')


@app.route('/rg_users')
@login_required
def reg_users():
    reg_us = Users.query.order_by(Users.id).all()
    return render_template('rg_users.html', reg_us=reg_us)


#@login_manager.user_loader
#def load_user(user_id):


@app.route('/login', methods=['POST', 'GET'])
def login():
    nick = request.form.get('nick')
    password = request.form.get('password')

    if nick and password:
        user_check = Users.query.filter_by(nick=nick).first()

        if user_check and check_password_hash(user_check.password, password):
            login_user(user_check)
            #next_page=request.args.get('next')
            #redirect(next_page)
            return redirect('/')
        else:
            flash('Login or pass is not correct')

    else:
        flash('Please fill the boxes')

    return render_template('login.html')


@app.route('/add_post', methods=['POST', 'GET'])
#@login_required
def post():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        file = save_img(request.files['photo'])
        file2 = save_img(request.files['photo2'])
        file3 = save_img(request.files['photo3'])
        file4 = save_img(request.files['photo4'])
        file5 = save_img(request.files['photo5'])
        #photo_type = file.mimetype
        category = request.form['category']
        active = True
        hostel = request.form['hostel']

        newfile = Post(name=name, description=description, image=file, image2=file2, image3=file3, image4=file4,
                       image5=file5, author=current_user, category=category, pub_date=datetime.now(), active=active,
                       hostel=hostel)
        #newfoto=Photo(photo_name=name, post_photo=file.read(), post_photo_type=photo_type)
        try:
            db.session.add(newfile)
            #db.session.add(newfoto)
            db.session.commit()
            return redirect('/main')
        except:
            return 'ERROR'
    else:
        #return 'Success'
        return render_template('add.html')

@app.route('/post/<int:id>')
def show_post(id):
    post = Post.query.get(id)
    return render_template('posts.html', post=post)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')
if __name__ =='__main__':
    app.run(debug=True)

'''@app.route('/<int:id>')
def get_img(id):
    #img = Photo.query.filter_by(id=id).first
    return Response(img.post_photo, mimetype=img.post_photo_type)
'''