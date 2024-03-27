from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os


main_file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(main_file_path)
database_file_path = os.path.join(directory_path, 'shop.db')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_file_path}'
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.title

@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)

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


if __name__ == "__main__":
    app.run(debug=True)