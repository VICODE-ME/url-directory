from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)
DATABASE = 'bookmarks.db'

def get_db():
    """Get a database connection with row factory."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Create the bookmarks table if it doesn't exist and seed with sample data."""
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                date_added TEXT NOT NULL,
                date_modified TEXT NOT NULL
            )
        ''')
        # Check if table is empty, seed if needed
        cur = db.execute('SELECT COUNT(*) FROM bookmarks')
        if cur.fetchone()[0] == 0:
            now = datetime.utcnow().isoformat() + 'Z'
            sample = [
                ('1', 'Internet Archive', 'https://archive.org', now, now),
                ('2', 'Project Gutenberg', 'https://gutenberg.org', now, now),
                ('3', 'Old Web Today', 'https://oldweb.today', now, now)
            ]
            db.executemany('INSERT INTO bookmarks VALUES (?,?,?,?,?)', sample)

def row_to_dict(row):
    """Convert a sqlite3.Row to a dictionary with camelCase keys."""
    return {
        'id': row['id'],
        'name': row['name'],
        'url': row['url'],
        'dateAdded': row['date_added'],
        'dateModified': row['date_modified']
    }

# Initialize the database on startup
init_db()

@app.route('/')
def index():
    """Serve the frontend HTML."""
    return render_template('index.html')

@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    """Return all bookmarks as JSON with camelCase keys."""
    db = get_db()
    rows = db.execute('SELECT * FROM bookmarks').fetchall()
    bookmarks = [row_to_dict(row) for row in rows]
    return jsonify(bookmarks)

@app.route('/api/bookmarks', methods=['POST'])
def add_bookmark():
    """Add a new bookmark."""
    data = request.get_json()
    now = datetime.utcnow().isoformat() + 'Z'
    new_id = str(uuid.uuid4())

    db = get_db()
    db.execute('INSERT INTO bookmarks VALUES (?,?,?,?,?)',
               (new_id, data['name'], data['url'], now, now))
    db.commit()

    created = {
        'id': new_id,
        'name': data['name'],
        'url': data['url'],
        'dateAdded': now,
        'dateModified': now
    }
    print(f"[POST] Added bookmark: {created}")  # Debug output
    return jsonify(created), 201

@app.route('/api/bookmarks/<id>', methods=['PUT'])
def update_bookmark(id):
    """Update an existing bookmark."""
    data = request.get_json()
    now = datetime.utcnow().isoformat() + 'Z'

    db = get_db()
    # Retrieve the original date_added
    cur = db.execute('SELECT date_added FROM bookmarks WHERE id = ?', (id,))
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'Bookmark not found'}), 404

    date_added = row['date_added']
    db.execute('''
        UPDATE bookmarks
        SET name = ?, url = ?, date_modified = ?
        WHERE id = ?
    ''', (data['name'], data['url'], now, id))
    db.commit()

    updated = {
        'id': id,
        'name': data['name'],
        'url': data['url'],
        'dateAdded': date_added,
        'dateModified': now
    }
    print(f"[PUT] Updated bookmark: {updated}")
    return jsonify(updated)

@app.route('/api/bookmarks/<id>', methods=['DELETE'])
def delete_bookmark(id):
    """Delete a bookmark."""
    db = get_db()
    db.execute('DELETE FROM bookmarks WHERE id = ?', (id,))
    db.commit()
    print(f"[DELETE] Deleted bookmark {id}")
    return '', 204

if __name__ == '__main__':
    # Run the Flask development server on all interfaces
    app.run(host='0.0.0.0', port=8802, debug=True)