from .base import db

class LoadOwner(db.Model):
    __tablename__ = 'load_owner'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    trips = db.relationship('Trip', backref='load_owner', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }