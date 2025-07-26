from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DistributionCenter(db.Model):
    __tablename__ = 'distribution_centers'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Float)
    longitude= db.Column(db.Float)

class Product(db.Model):
    __tablename__ = 'products'
    id                     = db.Column(db.Integer, primary_key=True)
    cost                   = db.Column(db.Float)
    category               = db.Column(db.String)
    name                   = db.Column(db.String)
    brand                  = db.Column(db.String)
    retail_price           = db.Column(db.Float)
    department             = db.Column(db.String)
    sku                    = db.Column(db.String)
    distribution_center_id = db.Column(db.Integer, db.ForeignKey('distribution_centers.id'))

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    id                             = db.Column(db.Integer, primary_key=True)
    product_id                     = db.Column(db.Integer, db.ForeignKey('products.id'))
    created_at                     = db.Column(db.DateTime)
    sold_at                        = db.Column(db.DateTime)
    cost                           = db.Column(db.Float)
    product_category               = db.Column(db.String)
    product_name                   = db.Column(db.String)
    product_brand                  = db.Column(db.String)
    product_retail_price           = db.Column(db.Float)
    product_department             = db.Column(db.String)
    product_sku                    = db.Column(db.String)
    product_distribution_center_id = db.Column(db.Integer, db.ForeignKey('distribution_centers.id'))

class Order(db.Model):
    __tablename__ = 'orders'
    order_id    = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer)
    status      = db.Column(db.String)
    gender      = db.Column(db.String)
    created_at  = db.Column(db.DateTime)
    returned_at = db.Column(db.DateTime)
    shipped_at  = db.Column(db.DateTime)
    delivered_at= db.Column(db.DateTime)
    num_of_item = db.Column(db.Integer)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id               = db.Column(db.Integer, primary_key=True)
    order_id         = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    user_id          = db.Column(db.Integer)
    product_id       = db.Column(db.Integer)
    inventory_item_id= db.Column(db.Integer)
    status           = db.Column(db.String)
    created_at       = db.Column(db.DateTime)
    shipped_at       = db.Column(db.DateTime)
    delivered_at     = db.Column(db.DateTime)
    returned_at      = db.Column(db.DateTime)
    sale_price       = db.Column(db.Float)

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    first_name    = db.Column(db.String)
    last_name     = db.Column(db.String)
    email         = db.Column(db.String)
    age           = db.Column(db.Integer)
    gender        = db.Column(db.String)
    state         = db.Column(db.String)
    street_address= db.Column(db.String)
    postal_code   = db.Column(db.String)
    city          = db.Column(db.String)
    country       = db.Column(db.String)
    latitude      = db.Column(db.Float)
    longitude     = db.Column(db.Float)
    traffic_source= db.Column(db.String)
    created_at    = db.Column(db.DateTime)

class ConversationSession(db.Model):
    __tablename__ = 'conversation_sessions'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer)
    started_at = db.Column(db.DateTime)

class Message(db.Model):
    __tablename__ = 'messages'
    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('conversation_sessions.id'))
    role       = db.Column(db.String)  # 'user' or 'ai'
    content    = db.Column(db.Text)
    timestamp  = db.Column(db.DateTime)
