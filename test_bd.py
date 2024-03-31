from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_login import LoginManager, login_required, UserMixin, login_user, current_user, logout_user
from datetime import datetime
import os
from werkzeug.security import generate_password_hash,  check_password_hash


main_file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(main_file_path)
database_file_path = os.path.join(directory_path, 'shop_test2.db')


images = UploadSet('images', IMAGES)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_epta'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_file_path}'
app.config['UPLOADED_IMAGES_DEST'] = 'static/media'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)
configure_uploads(app, images)

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)

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
    
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default='User')

    def __repr__(self):
        return f'User id: {self.id}\nUser name: {self.name}'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
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
    if current_user.status == 'Admin':
        items = Item.query.order_by(Item.category).all()
        return render_template('create.html', data=items)
    else:
        return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    users = Users.query.all()
    return render_template('profile.html')

@app.route('/orders')
@login_required
def orders():
    if current_user.status == 'Admin':
        orders = Order.query.order_by(Order.date).all()
        users = Users.query.all()
        return render_template('orders.html', data=orders, user=users)
    else:
        return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if current_user.status == 'Admin':
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
    else:
        return redirect(url_for('index'))
    
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
    
@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = Users.query.filter_by(name=name).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            return 'Dolbaeb'
    return render_template('login.html')

@app.route('/register/', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        status = request.form['status']
        user = Users(name=name, email=email, status=status)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('orders'))
    return render_template('register.html')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)