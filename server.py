from flask import Flask, jsonify, render_template, send_from_directory
import json
import os

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ticket-viewer.html')
def ticket_viewer():
    return render_template('ticket-viewer.html')

@app.route('/database.json')
def get_database():
    with open('database.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run()
