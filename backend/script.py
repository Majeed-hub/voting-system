from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



def init_db():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS candidates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 photo_address TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 candidate_id INTEGER,
                 FOREIGN KEY (candidate_id) REFERENCES candidates (id))''')

    conn.commit()
    conn.close()

# Create a new candidate
@app.route('/candidates', methods=['POST'])
def add_candidate():
    data = request.json
    name = data.get('name')
    photo_address = data.get('photo_address')
    print(photo_address)

    if name:
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()
        c.execute('INSERT INTO candidates (name, photo_address) VALUES (?, ?)', (name, photo_address))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Candidate added successfully'}), 201
    else:
        return jsonify({'error': 'Candidate name is required'}), 400
    
    # Delete an assignment
@app.route("/remove/<int:id>", methods=["DELETE"])
def remove_candidate(id):
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM votes WHERE candidate_id=?", (id,))
    cursor.execute("DELETE FROM candidates WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Candidate removed successfully"}), 200
    
# Get all candidates
@app.route('/candidates', methods=['GET'])
def get_candidates():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('SELECT * FROM candidates')
    candidates = [{'id': row[0], 'name': row[1], 'photo_address' : row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(candidates)

# Vote for a candidate
@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    votes = data.get("votes")


    if votes:
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()

       
        for candidate_id in votes:
            c.execute('INSERT INTO votes (candidate_id) VALUES (?)', (candidate_id,))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Votes recorded successfully'}), 201
    else:
        return jsonify({'error': 'Selected candidates are required'}), 400

# Get vote count for each candidate
@app.route('/vote_count', methods=['GET'])
def get_vote_count():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('''SELECT candidates.id, candidates.name, COUNT(votes.id) as vote_count
                 FROM candidates LEFT JOIN votes
                 ON candidates.id = votes.candidate_id
                 GROUP BY candidates.id, candidates.name''')
    vote_count = [{'candidate_id': row[0], 'name': row[1], 'vote_count': row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(vote_count)



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
