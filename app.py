import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def inicio():
    conexao = sqlite3.connect("duelo_garagem.db")
    conexao.row_factory = sqlite3.Row

    carros = conexao.execute("SELECT * FROM carros").fetchall()

    conexao.close()

    return render_template("index.html", carros=carros)

if __name__ == "__main__":
    app.run(debug=True)