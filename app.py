from tkinter.tix import Select
from flask import Flask, render_template, request, flash, redirect, url_for, session
import flask_session as fse

from werkzeug.security import check_password_hash, generate_password_hash

from sqlalchemy import Column, Integer, String, select, create_engine, delete
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.pool import StaticPool

from static.core import Base, login_required
from static.schemas import User, Post, Like, Comment

from datetime import datetime

from io import BufferedReader
from imagekitio import ImageKit

import os
from dotenv import load_dotenv

imagekit = ImageKit(
    public_key='public_VM+xI15VLJRfGWHvZFEpGsFhGEY=',
    private_key='private_XL8b+8cUUa2cfieAfJJyd+rbVks=',
    url_endpoint = 'https://ik.imagekit.io/sbkw83iqg'
)

load_dotenv()

app = Flask(__name__)

app.config["DEBUG"] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "97614eff3f4c3a5a1e1e7c980573c8f1c36bcfcc687b4218bcd85cc19f533b64"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
fse.Session(app)

engine = create_engine("sqlite:///delaygram.db", echo=True, future=True, connect_args={"check_same_thread": False}, 
    poolclass=StaticPool)
Base.metadata.create_all(engine, checkfirst=True)

@app.route("/")
@login_required
def index():

    # test = User(username="Yello", _hash="password", pfp="https://dm.kaist.ac.kr/datasets/animal-10n/images/thumbs/01.jpg")
    # db.session.add(test)
    # db.session.commit()

    with Session(engine) as ss:

        user = select(User).where(User.id==session["user_id"])
        user = ss.execute(user).scalars().all()[0]

        posts = select(Post).order_by(Post.timestamp.desc())
        posts = ss.execute(posts).scalars().all()

        likes = select(Like).where(Like.userid==session["user_id"])
        likes = ss.execute(likes).scalars().all()
        likes = [x.postid for x in likes]


        posters = []
        likecount = []
        for post in posts:
            poster = select(User).where(User.id==post.userid)
            poster = ss.execute(poster).scalars().all()[0]
            posters.append(poster)

            like = select(Like).where(Like.postid==post.id)
            like = ss.execute(like).scalars().all()
            likecount.append(len(like))

    return render_template("index.html", posts=zip(posts, posters, likecount), user=user, likes=likes, isLogged=True)

@app.route("/profile")
@login_required
def profile():

    with Session(engine) as ss:

        # test = User(
        #     username="test",
        #     fullname="Test User",
        #     _hash="test",
        #     bio="This is a test user.",
        #     pfp="https://cdn.discordapp.com/attachments/746122311748419655/1011377624251125840/unknown.png",
        #     timestamp=datetime.now()
        # )

        # test2 = User(
        #     username="test2",
        #     fullname="Test User2",
        #     _hash="test2",
        #     bio="This is a test user.",
        #     pfp="https://cdn.discordapp.com/attachments/746122311748419655/1011377624251125840/unknown.png",
        #     timestamp=datetime.now()
        # )

        # session.add_all([test, test2])
        # # session.commit()
        user = select(User).where(User.id==session["user_id"])
        user = ss.execute(user).scalars().all()[0]

        posts = select(Post).where(Post.userid==session["user_id"]).order_by(Post.timestamp.desc())
        posts = ss.execute(posts).scalars().all()

        postcount = len(posts)
        

    return render_template("profile.html", user=user, posts=posts, postcount=postcount, isLogged=True)

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # register user

        username = request.form.get("username")
        fullname = request.form.get("fullname")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        print(username, fullname, password, confirm)
        
        if not username or not fullname or not password or not confirm:
            
            return redirect(url_for(".error", error="Please fill out all fields."))
        
        if not password == confirm:
            
            return redirect(url_for(".error", error="Passwords do not match."))
        
        if len(password) < 8:
                
            return redirect(url_for(".error", error="Password must be at least 8 characters."))
        
        with Session(engine) as session:

            stmt = select(User).where(User.username == username)

            if session.scalar(stmt):
                
                return redirect(url_for(".error", error="Username already exists."))
            
            else:

                user = User(
                    username=username,
                    fullname=fullname,
                    _hash=generate_password_hash(password),
                    bio="",
                    pfp="https://instastatistics.com/images/default_avatar.jpg",
                    timestamp=datetime.now()
                )

                session.add(user)
                session.commit()

                flash("Successfully logged in")
                return redirect(url_for(".index"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()
    
    if request.method == "POST":
        # login user

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            
            return redirect(url_for(".error", error="Please fill out all fields."))
        
        with Session(engine) as ss:

            stmt = select(User).where(User.username == username)

            if ss.scalar(stmt):

                user = ss.scalar(stmt)

                if check_password_hash(user._hash, password):
                    
                    session["user_id"] = user.id
                    flash("Successfully logged in")
                    return redirect(url_for(".index"))
                
                else:

                    return redirect(url_for(".error", error="Incorrect password."))
            
            else:

                return redirect(url_for(".error", error="Username does not exist."))
    
    return render_template("login.html", isLogged=False)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for(".login"))

@app.route("/search")
@login_required
def search():
    
    with Session(engine) as ss:

        # query
        users = select(User).where(User.username==request.args.get("username"))
        users = ss.execute(users).scalars().all()
        print(users)

        # logged in user
        user = select(User).where(User.id==session["user_id"])
        user = ss.execute(user).scalars().all()[0]
    
    return render_template("search.html", user=user, qusers=users, isLogged=True)

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():

    if request.method == "POST":
        # edit user

        fullname = request.form.get("fullname")
        bio = request.form.get("bio")
        username = request.form.get("username")
        pfp = request.form.get("pfp")

        with Session(engine) as ss:

            stmt = select(User).where(User.id==session["user_id"])
            user = ss.execute(stmt).scalars().all()[0]

            testForUsername = select(User).where(User.username==username)
            testForUsername = ss.execute(testForUsername).scalars().all()

            if testForUsername and testForUsername[0].id != user.id:
                    
                return redirect(url_for(".error", error="Username already exists."))

            user.fullname = fullname
            user.bio = bio
            user.pfp = pfp
            user.username = username

            ss.commit()

            return redirect(url_for(".profile"))
    
    return render_template("edit.html")

@app.route("/post", methods=["POST"])
@login_required
def post():

    with Session(engine) as ss:

        user = select(User).where(User.id==session["user_id"])
        user = ss.execute(user).scalars().all()[0]

        
        postImage = request.files["postImage"]
        postImage.name = postImage.filename + str(datetime.now())
        postImage = BufferedReader(postImage)

        upload = imagekit.upload(
            file=postImage,
            file_name=request.files["postImage"].filename + str(datetime.now())
        )
        print(upload)

        post = Post(
            userid=user.id,
            image=upload["response"]["url"],
            desc=request.form.get("postDesc"),
            timestamp=datetime.now()
        )

        ss.add(post)
        ss.commit()

    return redirect(url_for(".index"))

@app.route("/like", methods=["POST"])
@login_required
def like():
    
    if request.form.get("status") == "like":
        with Session(engine) as ss:
    
            user = select(User).where(User.id==session["user_id"])
            user = ss.execute(user).scalars().all()[0]
    
            post = select(Post).where(Post.id==request.form.get("post_id"))
            post = ss.execute(post).scalars().all()[0]

            post.likes += 1
    
            like = Like(
                userid=user.id,
                postid=post.id,
            )
    
            ss.add(like, post)
            ss.commit()
    
        return redirect(url_for(".index"))
    
    elif request.form.get("status") == "unlike":

        with Session(engine) as ss:

            user = select(User).where(User.id==session["user_id"])
            user = ss.execute(user).scalars().all()[0]

            post = select(Post).where(Post.id==request.form.get("post_id"))
            post = ss.execute(post).scalars().all()[0]

            post.likes -= 1

            stmt = delete(Like).where(Like.userid==user.id).where(Like.postid==post.id)
            ss.execute(stmt)
            ss.add(post)
            ss.commit()

        return redirect(url_for(".index"))

@app.route("/comment", methods=["POST"])
@login_required
def comment():

    if request.form.get("status") == "new":
        with Session(engine) as ss:

            user = select(User).where(User.id==session["user_id"])
            user = ss.execute(user).scalars().all()[0]

            post = select(Post).where(Post.id==request.form.get("post_id"))
            post = ss.execute(post).scalars().all()[0]

            post.comments += 1
    elif request.form.get("status") == "del":
        with Session(engine) as ss:

            user = select(User).where(User.id==session["user_id"])
            user = ss.execute(user).scalar().all()[0]

            post = select(Post).where(Post.id==request.form.get("post_id"))
            post = ss.execute(post).scalars().all()[0]

            post.comments -= 1

            comment = select(Comment).where(Comment.id==request.form.get("comment_id"))
            comment = ss.execute(comment).scalars().all()[0]

            stmt = delete(Comment).where(Comment.id==request.form.get("comment_id"))
            ss.execute(stmt)

        

@app.route("/error")
def error():
    return render_template("error.html", error=request.args['error'])

if __name__ == "__main__":
    app.run()
