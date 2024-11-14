from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)


def init_db():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    # c.execute("drop table candidates")
    # c.execute("drop table votes")


    # Create candidates table
    c.execute('''CREATE TABLE IF NOT EXISTS candidates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 Fname TEXT NOT NULL,
                 Lname TEXT NOT NULL,
                 photo_address TEXT)''')

    # Create votes table
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 candidate_id INTEGER,
                 voter_no INTEGER,
                 FOREIGN KEY (candidate_id) REFERENCES candidates (id))''')

    conn.commit()
    conn.close()

# Route to add a new candidate


@app.route('/candidates', methods=['POST'])
def add_candidate():
    data = request.json
    Fname = data.get('Fname')
    Lname = data.get('Lname')
    photo_address = data.get('photo_address')

    if Fname and Lname:
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()
        c.execute(
            'INSERT INTO candidates (Fname, Lname, photo_address) VALUES (?, ?, ?)', (Fname, Lname, photo_address))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Candidate added successfully'}), 201
    else:
        return jsonify({'error': 'Candidate name is required'}), 400

# Route to delete a candidate


@app.route("/remove/<int:id>", methods=["DELETE"])
def remove_candidate(id):
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM votes WHERE candidate_id=?", (id,))
    cursor.execute("DELETE FROM candidates WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Candidate removed successfully"}), 200

# Route to get all candidates


@app.route('/candidates', methods=['GET'])
def get_candidates():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('SELECT * FROM candidates')
    candidates = [{'id': row[0], 'Fname': row[1], 'Lname': row[2], 'photo_address': row[3]}
                  for row in c.fetchall()]
    conn.close()
    random.shuffle(candidates)
    return jsonify(candidates)

# Route to submit votes


@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    votes = data.get("votes")
    voter_no = data.get("voter_no")

    if not votes or not voter_no:
        return jsonify({'error': 'Selected candidates and voter number are required'}), 400

    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()

    # Check if voter has already voted
    c.execute('SELECT * FROM votes WHERE voter_no = ?', (voter_no,))
    if c.fetchone():
        conn.close()
        return jsonify({'error': 'This voter has already voted'}), 403

    # Record each vote for the voter
    for candidate_id in votes:
        c.execute('INSERT INTO votes (candidate_id, voter_no) VALUES (?, ?)',
                  (candidate_id, voter_no))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Votes recorded successfully'}), 201

# Route to get vote count for each candidate


@app.route('/vote_count', methods=['GET'])
def get_vote_count():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('''SELECT candidates.id, candidates.Fname,candidates.Lname, COUNT(votes.id) as vote_count, candidates.photo_address
                 FROM candidates LEFT JOIN votes
                 ON candidates.id = votes.candidate_id
                 GROUP BY candidates.id ORDER BY vote_count DESC''')
    vote_count = [{'candidate_id': row[0], 'Fname': row[1], 'Lname': row[2],
                   'vote_count': row[3], 'photo_address': row[4]} for row in c.fetchall()]
    conn.close()
    return jsonify(vote_count)  

# Route to get total voter count


@app.route('/voter_count', methods=['GET'])
def get_voter_count():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(DISTINCT voter_no) FROM votes')
    voter_count = c.fetchone()[0]
    conn.close()
    return jsonify({'total_voters': voter_count})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
