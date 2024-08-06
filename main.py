from flask import Flask, request
from flask import render_template

app = Flask(__name__)
app.secret_key = 'document_scanner_app'

@app.route('/')
def scandoc():
    return render_template('scanner.html')

@app.route('/about')
def about():
    return "Here will come some information about used sources for this website, such as udemy course business-card-reader-app :)"

if __name__ == "__main__":
    app.run(debug=True)