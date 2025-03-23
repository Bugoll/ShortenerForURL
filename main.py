
from shortener import app, db

from shortener.models import User, Link

with app.app_context():
    db.create_all()
    print('✅ Database initialized successfully!')

    
    

if __name__ == "__main__":
    app.run(debug=True)
