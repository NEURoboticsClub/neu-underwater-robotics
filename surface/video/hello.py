from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def split_view():
	return render_template('split_view.html')

@app.route('/single_view/<int:camera_id>')
def single_view(camera_id):
	return render_template('single_view.html')

