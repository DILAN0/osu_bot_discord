from flask import Flask, render_template, request, redirect,send_file
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/v/')
def videoplayer():
    return render_template('videoplayer.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
