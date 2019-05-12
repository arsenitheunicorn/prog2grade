from flask import Flask, render_template, request
from morphoparser3000 import main as mrphp

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def seite():
    if request.method == 'POST':
        sentence = request.form['tupotext']
        output = mrphp(sentence)
        return render_template('base.html', output=output)
    else:
        return render_template('base.html')

if __name__ == "__main__":
    app.run()