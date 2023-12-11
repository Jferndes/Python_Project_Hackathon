from flask import Flask, flash, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'test'

@app.get("/")
def index():
    return render_template('index.html')

@app.get('/transform/<word>')
def transform(word: str):
    return render_template('transform.html', reverseWord = word[::-1])


@app.get('/calcul/<HT>')
def calcul(HT: float):
    val = int(HT) * (1 + 1/5)
    return render_template('calcul.html', valeur=val)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)