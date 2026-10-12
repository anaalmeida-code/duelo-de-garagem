import sqlite3
from flask import Flask, render_template, request
import random

app = Flask(__name__)

@app.route("/")
def inicio():
    conexao = sqlite3.connect("duelo_garagem.db")
    conexao.row_factory = sqlite3.Row

    carros = conexao.execute("SELECT * FROM carros").fetchall()

    conexao.close()

    return render_template("index.html", carros=carros)


@app.route("/duelo")
def duelo():
    conexao = sqlite3.connect("duelo_garagem.db")
    conexao.row_factory = sqlite3.Row

    todos_carros = conexao.execute(
        "SELECT * FROM carros"
    ).fetchall()

    if len(todos_carros) < 2:
        conexao.close()
        return "É necessário ter pelo menos dois carros."

    carro1_id = request.args.get("carro1", type=int)
    carro2_id = request.args.get("carro2", type=int)
    atributo = request.args.get("atributo")

    atributos_validos = ["potencia", "velocidade", "zero_cem"]

    vencedor = None
    resultado = None

    if carro1_id is not None and carro2_id is not None:
        carros = conexao.execute(
            "SELECT * FROM carros WHERE id IN (?, ?)",
            (carro1_id, carro2_id)
        ).fetchall()

        if len(carros) != 2 or carro1_id == carro2_id:
            conexao.close()
            return "Carros inválidos para o duelo.", 400

        carros = sorted(
            carros,
            key=lambda carro: 0 if carro["id"] == carro1_id else 1
        )
    else:
        carros = random.sample(todos_carros, 2)

    conexao.close()

    if atributo in atributos_validos:
        valor1 = carros[0][atributo]
        valor2 = carros[1][atributo]

        if valor1 == valor2:
            resultado = "Empate! Os dois carros têm o mesmo desempenho."
        elif atributo == "zero_cem":
            vencedor = carros[0] if valor1 < valor2 else carros[1]
        else:
            vencedor = carros[0] if valor1 > valor2 else carros[1]
        if vencedor is not None:
            if vencedor["id"] == carros[0]["id"]:
                resultado = f"🏆 {vencedor['nome']} — VOCÊ VENCEU!"
            else:
                resultado = f"💻 {vencedor['nome']} — VOCÊ PERDEU!"

    return render_template(
        "duelo.html",
        carros=carros,
        resultado=resultado
    )


if __name__ == "__main__":
    app.run(debug=True)
