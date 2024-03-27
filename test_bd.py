from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads
from datetime import datetime
import os


main_file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(main_file_path)
database_file_path = os.path.join(directory_path, 'shop_test.db')


images = UploadSet('images', IMAGES)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_file_path}'
app.config['UPLOADED_IMAGES_DEST'] = 'media'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
configure_uploads(app, images)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=False)
    image_path = db.Column(db.String(255))  
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String, nullable=False) 

    def __repr__(self):
        return self.title

    
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     email = db.Column(db.String, nullable=False)
#     user_status = db.Column(db.String, nullable=False, default='User')

#     def __repr__(self):
#         return self.name

# class Order(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     client_number = db.Column(db.String, nullable-False)
#     product_title = db.Column(db.Integer, nullable=False)
#     order_status = db.Column(db.String, nullable=False, default='Не обработан')
#     paymen_status = db.Column(db.String, nullable=False, default='Не оплачен')
#     date = db.Column()

#     def __repr__(self):
#         return f'Заказ №{self.id} : {self.product_id}'

def generate_filename(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Текущая дата и время
    file_extension = os.path.splitext(filename)[1]  # Расширение файла
    return timestamp + file_extension

@app.route('/')
def index():
    items = Item.query.order_by(Item.category).all()
    return render_template('index.html', data=items)

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/create', methods = ['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        item = Item(title=title, price=price)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error'

    else:     
        return render_template('create.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'image' in request.files:
        filename = images.save(request.files['image'], name=generate_filename(request.files['image'].filename))
        is_active = True if request.form.get('isActive') else False
        item = Item(
            title=request.form['title'],
            price=request.form['price'],
            isActive=is_active,
            image_path=filename,
            description=request.form['description'],
            category=request.form['category']
        )
        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error'
    else:
        return render_template('upload.html')
    
@app.route('/buy/<string:title>')
def buy(title):
    return render_template('make_order.html', title=title)

if __name__ == "__main__":
    app.run(debug=True)