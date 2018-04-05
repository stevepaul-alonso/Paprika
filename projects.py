from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import base, Products, Reviews, Users, Purchases
import os, random
import base64
from PIL import Image
from io import BytesIO
from sqlalchemy.dialects.postgresql import array
from sqlalchemy import desc, and_, or_
import urllib.parse
from sqlalchemy.sql import func

import boto3
s3 = boto3.resource('s3')

app = Flask(__name__)

#--------------Credentials are Hashed for security Purposes ------------------------------------------#
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user='######',pw='######',url='######',db='######')

ADMIN_ID = json.loads(open('admin.json', 'r').read())[0]['ADMIN_USERNAME']
ADMIN_PW = json.loads(open('admin.json', 'r').read())[0]['PASSWORD']

engine = create_engine(DB_URL)
base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# ------------------------------------------- Checks for any warning message ---------------------------------------------
#------------------------------------------------ Shows admin-login page -------------------------------------------------
@app.route('/admin-login')
def admin_login():
	try:
		login_session['message']
	except:
		login_session['message'] = 'none'

	return render_template('admin_login.html', message=login_session['message'])

# ------ Validate credentials of admin login and redirects to add products page or back to admin auth with a warning message
@app.route('/admin-auth', methods=['POST'])
def admin_auth():
	admin_username = request.form['admin_username']
	admin_password = request.form['admin_password']
	if len(admin_username) == 0:
		login_session['message'] = "Enter an admin Username and Password to login"
	elif len(admin_password) == 0:
		login_session['message'] = "Enter an admin Username and Password to login"
	elif admin_username != ADMIN_ID:
		login_session['message'] = "Invalid Admin Username"
	elif admin_password != ADMIN_PW:
		login_session['message'] = "Invalid Admin Password"
	else:
		login_session['admin_login'] = 1
		return redirect('/add_products')

	return redirect('/admin-login')

# ------- Checks if admin is logged in
# ------ Shows add_products HTML 
@app.route('/add_products')
def add_products():
	try:
		if login_session['admin_login'] != 1:
			return redirect('/admin_login')
		elif login_session['admin_login'] == 1:
			return render_template('add_products.html')
	except:
		return redirect('/admin-login')

# -------- Adds newly added product info to database
@app.route('/add_product_info', methods=['POST'])
def add_product_info():
	img = []
	photos = json.loads(request.form['photos'])
	name = urllib.parse.quote(request.form['name'])
	for photo in photos:
		photo = name + str(photo)
		img.append(photo)
	product = Products(name = request.form['name'],
						cuisine = request.form['category'],
						restaurant = request.form['brand'],
						price = request.form['price'],
						quantity = request.form['quantity'],
						description = request.form['description'],
						photos = array(img),
						rating= 3
                )
	session.add(product)
	session.commit()
	return "success"

# -------- Adds images of newly added product to amazon s3
@app.route('/photo_upload', methods=['POST'])
def add_photos():
	images = ['image1', 'image2', 'image3', 'image4', 'image5', 'image6']
	name_base= urllib.parse.quote(request.form['name_base'])
	if len(name_base) > 1:
		for image in images:
			for file in request.files.getlist(image):
				blob = file.read()
				if(len(blob)>0):
					try:
						im = Image.open(BytesIO(blob))
						out_im2 = BytesIO()
						im.save(out_im2, 'JPEG',quality=90,optimize=True, progressive=True)
					except:
						im = Image.open(BytesIO(blob)).convert('RGB')
						out_im2 = BytesIO()
						im.save(out_im2, 'JPEG',quality=90,optimize=True, progressive=True)

					name=name_base+image.split('image')[1]+'.jpg'

					s3.Bucket('paprikasteve').put_object(Key=name, Body=out_im2.getvalue(), ACL= 'public-read')
	return redirect('/add_products')

# --------------------------------------------------- Checks if user is logged in --------------------------------------
# ------------------------------------------ Shows homepage HTML with cart and user info -------------------------------
@app.route('/')
def homepage():
	login_session['purchase'] = 0
	try:
		login_session['username']
		purchases = session.query(Purchases).filter(and_(Purchases.user_id == login_session['username'], Purchases.status == 0)).all()
		purchases_list = [row.serialize for row in purchases]
		for purchase in purchases:
			login_session['purchase']+=purchase.qty
	except:
		login_session['username'] = 'none'
		login_session['image'] = 'none'
		login_session['purchase'] = 0
	return render_template('homepage.html', name = login_session['username'], image = login_session['image'], qty = login_session['purchase'])

#-------------------------------- Fetch brands available based on filter to show on homepage ----------------------------
@app.route('/fetch_brands', methods = ['POST'])
def fetch_brands():
	restaurants = []
	cuisine = request.form['category']
	if cuisine == 'All':
		data = session.query(Products.restaurant).distinct().all()
	else:
		data = session.query(Products.restaurant).filter_by(cuisine = cuisine).distinct().all()
	for val in data:
		restaurants.append(val.restaurant)

	return jsonify(restaurants)

#--------------------------------------------- Fetch product data from server ---------------------------------
@app.route('/fetch_data', methods=['POST'])
def fetch_data():
	category = request.form['category']
	rating = request.form['rating']
	brand = request.form['brand']
	price = request.form['price']
	name = request.form['last_product']


	base_query = "session.query(Products).filter(and_(Products.cuisine_id >= 0"

	if category != 'All':
		base_query += ", Products.cuisine == '" + category + "'"
	if rating != 'any':
		base_query +=  ", Products.rating == '" + rating + "'"
	if brand != 'any':
		base_query +=  ", Products.restaurant == '" + brand + "'"
	if price == '0':
		base_query +=  ", Products.price <= " + '10'
	if price == '10':
		base_query +=  ", Products.price >= " + '10'
		base_query +=  ", Products.price <= " + '30'
	if price == '30':
		base_query +=  ", Products.price >= " + '30'
	if name != 'none':
		base_query += ", Products.name.ilike('%" + name +"%')"

	base_query += ")).limit(15).all()"

	data = eval(base_query)
	data = [row.serialize for row in data]

	for item in data:
		for i in range(1, len(item['photos'])+1):
			item['photos'][i-1] = (item['photos'][i-1]).replace('%', '%25')
	return jsonify(data)

#------------------------------------------------------ User Login ---------------------------------
#---------------------- Returns a message if credentials are not validate --------------------------
@app.route('/login', methods=['POST'])
def login():
	username = request.form['username']
	password = request.form['password']
	print(username, password)
	if username == '' or password == '':
		return "Username or Password is missing"
	else:
		try:
			user = session.query(Users).filter_by(user_name = username).all()
			print(user)
			user_details = [row.serialize for row in user]
			print(user_details)
			if (user_details[0]['password'] != password):
				return "Wrong Passwword"
			else:
				login_session['username'] = username
				login_session["image"] = 'img/common/' +str(user_details[0]['image'])+ '.png'
		except:
			return "You have not registered yet please do signup"


	return "success"

#------------------------------------------------------ User Signup ---------------------------------
# ----------------- Checks if user is already registered and sends a message ------------------------
#----------------------------- If user not registered adds him to database --------------------------
@app.route('/signup', methods=['POST'])
def signup():
	username = request.form['username'].replace(" ","")
	password = request.form['password'].replace(" ","")
	image = random.randint(0,3)

	if (username == '' or password == ''):
		return "Enter a username and password"
	try:
		user = session.query(Users).filter_by(user_name = username).first()
		user_details = user.serialize()
		return "Username already exist"
	except:
		user_info = Users(
			user_id = username,
			user_name = username,
			password = password,
			image = image
			)
		session.add(user_info)
		session.commit()
		login_session["image"] = 'img/common/' +str(image)+ '.png'
		login_session["username"] = username
	return "success"

#------------------------------------------ Adds selected item to cart ----------------------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
	product_id = int(request.form['product_id'])
	total_amount = request.form['total_amount'].split('$')[1]
	print(product_id)
	print(login_session['username'])
	try:
		if login_session["username"] != 'none':
			purchase_id = login_session['username'] + str(product_id)
		else:
			return "Please log in to add to cart"
	except:
		return "Please log in to add to cart"

	try:
		purchase = session.query(Purchases).filter_by(purchase_id = purchase_id).first()
		if purchase.status == 0:
			purchase.qty+=1
		else:
			purchase.qty=1
			purchase.status=0
		session.add(purchase)
		session.commit()

	except:
		purchase = Purchases(
			purchase_id = purchase_id,
			user_id = login_session['username'],
			item_id = product_id,
			qty = 1,
			total_amount = total_amount,
			status = 0
		)

		session.add(purchase)
		session.commit()

	return "Successfully added to cart"

#------------------------------------------ Shows product HTML page ----------------------------
@app.route('/product/<id>')
def product_page(id):
	login_session['purchase'] = 0
	try:
		login_session['username']
		purchases = session.query(Purchases).filter(and_(Purchases.user_id == login_session['username'], Purchases.status == 0)).all()
		purchases_list = [row.serialize for row in purchases]
		for purchase in purchases:
			login_session['purchase']+=purchase.qty
	except:
		login_session['username'] = 'none'
		login_session['image'] = 'none'
		login_session['purchase'] = 0
	cuisine_id = int(id)
	product = session.query(Products).filter_by(cuisine_id = cuisine_id).first()
	info = product.serialize
	for i in range(1, len(info['photos'])+1):
		info['photos'][i-1] = (info['photos'][i-1]).replace('%', '%25')
	return render_template('product.html',name=login_session['username'],image=login_session['image'],qty=login_session['purchase'], info= info)

#------------------------------------------ Shows Checkout HTML page ----------------------------------------------
@app.route('/cart')
def cart():
	login_session['purchase'] = 0
	payment = 0
	try:
		login_session['username']
		purchases = session.query(Purchases).filter(and_(Purchases.user_id == login_session['username'], Purchases.status == 0)).all()
		purchases_list = [row.serialize for row in purchases]
		for purchase in purchases:
			login_session['purchase']+=purchase.qty
	except:
		login_session['username'] = 'none'
		login_session['image'] = 'none'
		login_session['purchase'] = 0

	data = session.query(Purchases).filter(and_(Purchases.user_id == login_session['username'], Purchases.status == 0)).all()
	info = [row.serialize for row in data]
	for item in info:
		print(item)
		product = session.query(Products).filter_by(cuisine_id = item['item_id']).first()
		product = product.serialize
		item["item_name"] = product['name']
		item["total_amount"] = item["qty"] * item["total_amount"]
		payment += item["total_amount"]
		item["image"] = "https://s3.us-east-2.amazonaws.com/paprikasteve/" + product["photos"][0].replace('%', '%25') + ".jpg"

	return render_template('cart.html',name=login_session['username'],image=login_session['image'],qty=login_session['purchase'], info=info, payment=payment)


#----------------------------------------- Delete an item from cart -------------------------------------------------
@app.route('/delete_item', methods = ['POST'])
def delete_item():
	item_id = int(request.form['item_id'])
	item = session.query(Purchases).filter(and_(Purchases.user_id == login_session['username'], Purchases.item_id == item_id, Purchases.status == 0)).first()
	session.delete(item)
	session.commit()
	del login_session['purchase']
	return "success"

#----------------------------------------- Adds data of completed purchase -------------------------------------------
@app.route('/complete_purchase')
def complete_purchase():
	items = session.query(Purchases).filter(and_(Purchases.user_id == login_session['username'],Purchases.status == 0)).all()
	for item in items:
		item.status = 1
		session.add(item)
		session.commit()
	return "success"

#----------------------------------------- Adds rating information to database ---------------------------------------
@app.route('/rate', methods=['POST'])
def rate():
	product_id = request.form['product_id']
	rating = request.form['rating']
	review_id = product_id + login_session['username']

	print("product_id", product_id)
	print("review_id", review_id)

	print("rating", rating)

	if int(rating) < 0:
		rating = 0
	elif int(rating) > 5:
		rating=5

	try:
		login_session['username']
		if (login_session['username'] == 'none'):
			return "Please login to rate this item"
	except:
		return "Please login to rate this item"

	try:
		review = session.query(Reviews).filter_by(review_id = review_id).first()
		print(review.rating)
		return "You have already rated this product"
	except:
		pass

	review = Reviews(
			review_id = review_id,
			reviewer_id = login_session['username'],
			cuisine_id = product_id,
			review = "none",
			rating = rating
		)
	session.add(review)
	session.commit()

	test_data = session.query(func.avg(Reviews.rating).label('average')).filter_by(cuisine_id=product_id).one()
	avg_rating = int(test_data.average)


	product = session.query(Products).filter_by(cuisine_id = product_id).first()
	product.rating = avg_rating
	session.add(product)
	session.commit()
	return "Your rating was Successfully added"


#---------------------------------- Delete warning message after displaying -------------------------------------------
@app.route('/delete_warning')
def delete_warning():
	del login_session['message']
	return "success"
	 		
#---------------------------------- Start the app  -------------------------------------------
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
