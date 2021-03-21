import sqlite3
import bcrypt
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class DB:
    def __init__(self, db_name):
        self.db_name = db_name

    def create_user_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE users 
                        (id integer PRIMARY KEY,
                        username text UNIQUE NOT NULL,
                        email text UNIQUE NOT NULL,
                        image_file text DEFAULT 'default.jpg',
                        password text NOT NULL)''')
        conn.commit()
        conn.close()

    def create_posts_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE posts 
                                (id integer PRIMARY KEY,
                                title text NOT NULL,
                                content text NOT NULL,
                                date date NOT NULL,
                                u_id integer)''')
        conn.commit()
        c.close()
        conn.close()

    def add_user(self, username, email, password):
        encoded_pw = password.encode('utf-8')
        hashed_pw = bcrypt.hashpw(encoded_pw, bcrypt.gensalt())
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        data = (username, email, hashed_pw)
        try:
            c.execute('''INSERT INTO users (username, email, password)
                            VALUES (?, ?, ?)''', data)
            conn.commit()
            c.close()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.commit()
            c.close()
            conn.close()
            return False

    def add_post(self, user_id, title, content):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        dt_object = datetime.utcnow()
        if dt_object.month < 10:
            date = str(dt_object.year) + '-' + '0' + str(dt_object.month) + '-' + str(dt_object.day)
        else:
            date = str(dt_object.year) + '-' + str(dt_object.month) + '-' + str(dt_object.day)
        data = (title, content, date, user_id)
        c.execute('''INSERT INTO posts (title, content, date, u_id)
                        VALUES (?, ?, ?, ?)''', data)
        conn.commit()
        c.close()
        conn.close()

    def is_email(self, email):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT password FROM users
                                WHERE email=?''', (email,))
        emails = c.fetchone()
        c.close()
        conn.close()
        if emails is None:
            return False
        else:
            return True

    def is_username(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT password FROM users
                                WHERE username=?''', (username,))
        usernames = c.fetchone()
        c.close()
        conn.close()
        if usernames is None:
            return False
        else:
            return True

    def check_login(self, username, password):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT password FROM users
                        WHERE username=?''', (username,))
        try:
            hashed_pd = c.fetchone()[0]
        except TypeError:
            return False
        c.close()
        conn.close()
        return bcrypt.checkpw(password.encode('utf-8'), hashed_pd)

    def get_posts(self, username=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if username is None:
            c.execute('''SELECT users.username, posts.title, posts.content, posts.date
                            FROM users
                            JOIN posts
                            ON users.id=posts.u_id
                            ORDER BY date DESC''')
        else:
            c.execute('''SELECT posts.title, posts.content, posts.date
                            FROM users
                            JOIN posts
                            ON users.id=posts.u_id
                            WHERE users.username=?
                            ORDER BY date DESC''', (username, ))
        posts = c.fetchall()
        c.close()
        conn.close()
        return posts

    def update_picture(self, picture, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''UPDATE users SET image_file=? WHERE username=?''', (picture, username))
        conn.commit()
        c.close()
        conn.close()

    def get_id(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT id FROM users
                                WHERE username=?''', (username,))
        user_id = c.fetchone()[0]
        c.close()
        conn.close()
        return user_id

    def get_email(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT email FROM users
                                WHERE username=?''', (username,))
        email = c.fetchone()[0]
        c.close()
        conn.close()
        return email

    def get_image(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''SELECT image_file FROM users
                                WHERE username=?''', (username,))
        image = c.fetchone()[0]
        c.close()
        conn.close()
        return image

    def reset_pw(self, user_id, password):
        encoded_pw = password.encode('utf-8')
        hashed_pw = bcrypt.hashpw(encoded_pw, bcrypt.gensalt())
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''UPDATE users
                        SET password=?
                        WHERE username=?''', (hashed_pw, user_id))
        conn.commit()
        c.close()
        conn.close()


class User(UserMixin):

    def __init__(self, username):
        db = DB('site.db')
        self.username = username
        self.id = username
        self.email = db.get_email(self.username)
        self.user_id = db.get_id(self.username)
        self.image = db.get_image(self.username)

    def get_posts(self):
        db = DB('site.db')
        return db.get_posts(self.username)

    def reset_pass(self):
        s = Serializer('saksham2001', 1800)
        return s.dumps({'user_id': self.user_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer('saksham2001')
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return user_id
