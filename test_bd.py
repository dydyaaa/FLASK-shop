from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads
from datetime import datetime
import os


main_file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(main_file_path)
database_file_path = os.path.join(directory_path, 'shop_test2.db')


images = UploadSet('images', IMAGES)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_file_path}'
app.config['UPLOADED_IMAGES_DEST'] = 'static/media'
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

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_number = db.Column(db.String, nullable=False)
    client_name = db.Column(db.String, nullable=False)
    product_title = db.Column(db.Integer, nullable=False)
    order_status = db.Column(db.String, nullable=False, default='Не обработан')
    paymen_status = db.Column(db.String, nullable=False, default='Не оплачен')
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return self.product_title
    
with app.app_context():
    db.create_all()

def generate_filename(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  
    file_extension = os.path.splitext(filename)[1]  
    return timestamp + file_extension

@app.route('/')
def index():
    items = Item.query.order_by(Item.category).all()
    return render_template('index.html', data=items)

@app.route('/create')
def create():
    items = Item.query.order_by(Item.category).all()
    return render_template('create.html', data=items)

@app.route('/orders')
def orders():
    orders = Order.query.order_by(Order.date).all()
    return render_template('orders.html', data=orders)

@app.route('/about')
def about():
    return render_template('about.html')

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
    
@app.route('/order_accepted/<int:order_id>')
def order_accepted(order_id):
    return render_template('OK_order.html', id=order_id)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    record = Item.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('create'))

@app.route('/update_order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    item = Item.query.get_or_404(order_id)
    item.title = request.form['title']
    item.price = request.form['price']
    item.description = request.form['description']
    item.category = request.form['category']
    item.isActive = True if request.form.get('isActive') else False
    db.session.commit()
    return redirect(url_for('create'))

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form['status']
    order.order_status = new_status
    db.session.commit()
    return redirect(url_for('orders'))

@app.route('/update_paymen_status/<int:order_id>', methods=['POST'])
def update_paymen_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form['status']
    order.paymen_status = new_status
    db.session.commit()
    return redirect(url_for('orders'))

@app.route('/buy/<string:title>', methods=['GET', 'POST'])
def buy(title):
    if request.method == 'POST':
        order = Order(
            client_number=request.form['client_phone'],
            client_name=request.form['client_name'],
            product_title=title
        )
        try:
            db.session.add(order)
            db.session.commit()
            last_order = Order.query.order_by(Order.id.desc()).first()
            return redirect(url_for('order_accepted', order_id=last_order.id))
        except:
            return 'Error'
    else:
        return render_template('make_order.html', title=title)

if __name__ == "__main__":
    app.run(debug=True)