from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# DB connection string
# <protocol>://<user>:<pass>@<host>:<port>/<db_name>
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://orm_dev:123456@localhost:5432/orm_db'

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model
# This just declares and configures the model in memory - the physical DB is unaffected.
class Product(db.Model):
    __tablename__ = "Products"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float(precision=2))
    stock = db.Column(db.Integer, db.CheckConstraint('stock >= 0'))    

# Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'stock')


@app.route('/')
def home():
    return 'Hello!'

# R - Read (all)
@app.route('/products')
def get_all_products():
    # Generate a statement
    # SELECT * FROM products;
    stmt = db.select(Product)
    # Execute the statement
    products = db.session.scalars(stmt)
    return ProductSchema(many=True).dump(products)

# R - Read (one)
@app.route('/products/<int:product_id>')
def get_one_product(product_id):
    # Get Product with given id
    # SELECT * FROM products WHERE id = product_id;
    stmt = db.select(Product).filter_by(id=product_id)
    product = db.session.scalar(stmt)
    if product:
        return ProductSchema().dump(product)
    else:
        return {"error": f"Product with id {product_id} not found"}, 404

# C - Create (one)
@app.route('/products', methods=['POST'])
def create_product():
    # Parse the incoming JSON body to a dict
    data = ProductSchema().load(request.json)
    # Create a new instance
    new_product = Product(
        name = data['name'],
        description = data['description'],
        price = data['price'],
        stock = data['stock']
    )
    # Add to db session
    db.session.add(new_product)
    # Commit to the db
    db.session.commit()
    # Return the new product
    return ProductSchema().dump(new_product)


# U - Update one product
# 1. Create statement to select the product with the given product_id
# 2. Execute the statement (scalar)

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_one_product(product_id):
    stmt = db.select(Product).filter_by(id=product_id)
    product = db.session.scalar(stmt)

    if product:
        data = ProductSchema().load(request.json, partial=True)
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'stock' in data:
            product.stock = data['stock']

        db.session.commit()
        return ProductSchema().dump(product), 200
    else:
        return {"error": f"Product with id {product_id} not found"}, 404

    
    
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_one_product(product_id):
    stmt = db.select(Product).filter_by(id=product_id)
    product = db.session.scalar(stmt)

    if product:
        db.session.delete(product)
        db.session.commit()
        return {}, 204  # 204 No Content
    else:
        return {"error": f"Product with id {product_id} not found"}, 404



@app.cli.command('init_db')
def init_db():
    db.drop_all()
    db.create_all()
    print('Created tables')

@app.cli.command('seed_db')
def seed_db():
    products = [
        Product(
            name='Wireless Mouse',
            description='Ergonomic wireless mouse with adjustable DPI and long battery life.',
            price=25.99,
            stock=100
        ),
        Product(
            name='Gaming Keyboard',
            description='Mechanical keyboard with RGB lighting and programmable keys.',
            price=89.99,
            stock=50
        ),
        Product(
            name='HD Monitor',
            description='27-inch full HD monitor with ultra-thin bezels and vivid colors.',
            price=179.99,
            stock=30
        ),
        Product(
            name='USB-C Hub',
            description='Multiport adapter offering HDMI, USB 3.0, and Ethernet connections.',
            price=39.99,
            stock=200
        ),
        Product(
            name='External Hard Drive',
            description='2TB portable external hard drive with fast data transfer speeds.',
            price=64.99,
            stock=80
        ),
        Product(
            name='Bluetooth Speaker',
            description='Portable speaker with deep bass, crisp sound quality, and water resistance.',
            price=45.50,
            stock=120
        ),
        Product(
            name='Smartwatch',
            description='Fitness tracker smartwatch with heart rate monitoring and GPS.',
            price=99.99,
            stock=70
        ),
        Product(
            name='Laptop Stand',
            description='Adjustable aluminum laptop stand for ergonomic comfort and cooling.',
            price=29.99,
            stock=150
        ),
        Product(
            name='Wireless Earbuds',
            description='True wireless earbuds featuring noise cancellation and long battery life.',
            price=59.99,
            stock=90
        ),
        Product(
            name='Portable Charger',
            description='10,000mAh power bank with fast charging capabilities and multiple ports.',
            price=19.99,
            stock=250
        ),
    ]

    db.session.add_all(products)
    db.session.commit()
    print('DB Seeded with 10 products')


    # db.delete(Product)
    db.session.add_all(products)

    db.session.commit()

    print('DB Seeded')