from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, LargeBinary
from static.core import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, nullable=False)
    fullname = Column(String, nullable=False)
    _hash = Column(String, nullable=False)
    bio = Column(String(200))
    pfp = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.id'), nullable=False)
    image = Column(String, nullable=False)
    desc = Column(String, nullable=False)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    timestamp = Column(DateTime, nullable=False)

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.id'), nullable=False)
    postid = Column(Integer, ForeignKey('posts.id'), nullable=False)
    comment = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.id'), nullable=False)
    postid = Column(Integer, ForeignKey('posts.id'), nullable=False)

class Follow(Base):
    __tablename__ = 'follows'
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.id'), nullable=False)
    followingid = Column(Integer, ForeignKey('users.id'), nullable=False)
