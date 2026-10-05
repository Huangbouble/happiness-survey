# -*- coding: utf-8 -*-
# 当代大学生幸福指数调查 —— 后台收集服务
# 运行：pip install -r requirements.txt  然后  python app.py
# 打开：http://127.0.0.1:5000
from flask import Flask, request, jsonify, send_file, Response
import sqlite3, json, csv, io, os, datetime
import urllib.request

GOOGLE_URL = 'https://script.google.com/macros/s/AKfycbycIdiW-rQXsFOYS8cGMY-e2fgk0K5EbnZY2WmvbsRI2g-bkN3La9gsZFch_6ZtcerlHg/exec'

DB = 'happiness.db'
ADMIN_KEY = '100426h'  
REQUIRED = ['b0','b1','b2','b3','b4','c1','c2','c3','c4','c5','c6','c7','c8','d1','d2']
FIELDS = REQUIRED + ['a1','a2','a3','a4','a5','a6']

def init_db():
    con = sqlite3.connect(DB)
    con.execute('''CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, score INTEGER, payload TEXT)''')
    con.commit(); con.close()

app = Flask(__name__, static_folder='.', static_url_path='')

@app.get('/')
def home():
    return send_file('index.html')

@app.post('/api/submit')
def submit():
    data = request.get_json(force=True, silent=True) or {}
    missing = [k for k in REQUIRED if data.get(k) in (None, '')]
    if missing:
        return jsonify({'ok': False, 'msg': 'missing: ' + ','.join(missing)}), 400
    ts = datetime.datetime.now().isoformat(timespec='seconds')
    con = sqlite3.connect(DB)
    con.execute('INSERT INTO responses(ts,score,payload) VALUES(?,?,?)',
                (ts, data.get('score'), json.dumps(data, ensure_ascii=False)))
    con.commit(); con.close()
    return jsonify({'ok': True})

@app.get('/api/count')
def count():
    con = sqlite3.connect(DB)
    n = con.execute('SELECT COUNT(*) FROM responses').fetchone()[0]
    con.close()
    return jsonify({'count': n})

@app.get('/api/export.csv')
def export():
    if request.args.get('key') != ADMIN_KEY:
        return 'forbidden', 403
    con = sqlite3.connect(DB)
    rows = con.execute('SELECT ts, score, payload FROM responses ORDER BY id').fetchall()
    con.close()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(['ts', 'score'] + FIELDS)
    for ts, score, payload in rows:
        d = json.loads(payload)
        w.writerow([ts, score] + [d.get(k, '') for k in FIELDS])
    return Response('﻿' + buf.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=happiness_data.csv'})

init_db()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
