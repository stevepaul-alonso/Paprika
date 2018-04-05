import sys
import psycopg2
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

base = declarative_base()

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user='######',pw='######',url='######',db='######')

class Products(base):
	__tablename__ = 'products'
	cuisine_id = Column(Integer, primary_key = True)
	name = Column(String(150))
	cuisine = Column(String(150))
	description = Column(String())
	photos = Column(ARRAY(String(80)))
	restaurant = Column(String(250))
	price = Column(Float)
	quantity = Column(Integer)
	rating = Column(Integer)

	@property
	def serialize(self):
		return {
           'cuisine_id': self.cuisine_id,
           'name': self.name,
           'cuisine': self.cuisine,
           'description': self.description,
           'photos': self.photos,
           'restaurant': self.restaurant,
           'price': self.price,
           'quantity': self.quantity,
           'rating':self.rating
		}


class Reviews(base):
	__tablename__ = 'reviews'
	review_id = Column(String(150), nullable  = False, primary_key = True)
	cuisine_id = Column(String(250))
	reviewer_id = Column(String(150))
	review = Column(String())
	rating = Column(Float)

	@property
	def serialize(self):
		return {
           'review_id': self.review_id,
           'cuisine_id': self.cuisine_id,
           'reviewer_id': self.reviewer_id,
           'review': self.review,
           'rating': self.rating
		}

class Purchases(base):
	__tablename__ = 'purchases'
	purchase_id = Column(String(200), primary_key = True)
	user_id = Column(String(150), nullable  = False)
	item_id = Column(Integer)
	qty = Column(Integer)
	total_amount = Column(Float)
	status = Column(Integer)

	@property
	def serialize(self):
		return {
           'user_id': self.user_id,
           'item_id': self.item_id,
           'qty': self.qty,
           'total_amount': self.total_amount,
           'status': self.status
		}

class Users(base):
	__tablename__ = 'users'
	user_id = Column(String(), primary_key = True)
	user_name = Column(String())
	password = Column(String())
	image = Column(Integer)

	@property
	def serialize(self):
		return {
           'user_id': self.user_id,
           'user_name': self.user_name,
           'password': self.password,
           'image': self.image
	}


engine = create_engine(DB_URL)
base.metadata.create_all(engine)
