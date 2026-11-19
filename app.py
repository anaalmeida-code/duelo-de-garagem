
import sqlite3
import random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "duelo-garagem-chave-desenvolvimento"


def buscar_carros():
    conexao = sqlite3.connect("duelo_garagem.db")
    conexao.row_factory = sqlite3.Row

    carros = conexao.execute(
        "SELECT * FROM carros"
    ).fetchall()

    conexao.close()
    return carros


@app.route("/")
def inicio():
    carros = buscar_carros()
    return render_template("index.html", carros=carros)


@app.route("/nova-partida")
def nova_partida():
    session.clear()

    session["rodada"] = 1
    session["vitorias_jogador"] = 0
    session["vitorias_computador"] = 0
    session["empates"] = 0
    session["rodada_contabilizada"] = False
    session["partida_finalizada"] = False

    return redirect(url_for("duelo"))


@app.route("/proxima-rodada")
def proxima_rodada():
    if "rodada" not in session:
        return redirect(url_for("nova_partida"))

    if session.get("partida_finalizada"):
        return redirect(url_for("duelo"))

    if not session.get("rodada_contabilizada"):
        return redirect(url_for("duelo"))

    if session["rodada"] < 5:
        session["rodada"] += 1
        session["rodada_contabilizada"] = False

        session.pop("carros_rodada", None)
        session.pop("resultado_rodada", None)
        session.pop("atributo_escolhido", None)
        session.pop("vencedor_rodada", None)

        return redirect(url_for("duelo"))

    session["partida_finalizada"] = True
    return redirect(url_for("duelo"))


@app.route("/duelo", methods=["GET", "POST"])
def duelo():
    if "rodada" not in session:
        return redirect(url_for("nova_partida"))

    todos_carros = buscar_carros()

    if len(todos_carros) < 2:
        return "É necessário ter pelo menos dois carros."

    if "carros_rodada" not in session:
        sorteados = random.sample(todos_carros, 2)

        session["carros_rodada"] = [
            sorteados[0]["id"],
            sorteados[1]["id"]
        ]

    ids = session["carros_rodada"]

    carros = [
        next(
            (carro for carro in todos_carros
             if carro["id"] == id_carro),
            None
        )
        for id_carro in ids
    ]

    if any(carro is None for carro in carros):
        return "Um dos carros da rodada não foi encontrado.", 400

    rodada = session["rodada"]

    # Rodadas pares sao do computador
    vez_computador = rodada % 2 == 0

    atributos_validos = [
        "potencia",
        "velocidade",
        "zero_cem"
    ]

    resultado = session.get("resultado_rodada")

    # O duelo so acontece quando o botao e clicado
    if (
        request.method == "POST"
        and not session["rodada_contabilizada"]
        and not session["partida_finalizada"]
    ):

        if vez_computador:
            # Computador escolhe aleatoriamente
            atributo = random.choice(atributos_validos)
        else:
            # Jogador escolhe o atributo
            atributo = request.form.get("atributo")

        if atributo in atributos_validos:

            valor1 = carros[0][atributo]
            valor2 = carros[1][atributo]

            if valor1 == valor2:
                resultado = (
                    "🤝 Empate! Os dois carros "
                    "têm o mesmo desempenho."
                )
                session["empates"] += 1
                session["vencedor_rodada"] = "empate"

            elif (
                (atributo == "zero_cem" and valor1 < valor2)
                or
                (atributo != "zero_cem" and valor1 > valor2)
            ):
                resultado = (
                    f"🏆 {carros[0]['nome']} "
                    "— VOCÊ VENCEU!"
                )
                session["vitorias_jogador"] += 1
                session["vencedor_rodada"] = "jogador"

            else:
                resultado = (
                    f"💻 {carros[1]['nome']} "
                    "— VOCÊ PERDEU!"
                )
                session["vitorias_computador"] += 1
                session["vencedor_rodada"] = "computador"

            session["resultado_rodada"] = resultado
            session["atributo_escolhido"] = atributo
            session["rodada_contabilizada"] = True

            return redirect(url_for("duelo"))

    vitorias_jogador = session["vitorias_jogador"]
    vitorias_computador = session["vitorias_computador"]
    empates = session["empates"]

    resultado_final = None

    if session["partida_finalizada"]:

        if vitorias_jogador > vitorias_computador:
            resultado_final = (
                "🏆 PARABÉNS! VOCÊ VENCEU A PARTIDA!"
            )

        elif vitorias_computador > vitorias_jogador:
            resultado_final = (
                "💻 O COMPUTADOR VENCEU A PARTIDA!"
            )

        else:
            resultado_final = (
                "🤝 A PARTIDA TERMINOU EMPATADA!"
            )

    return render_template(
        "duelo.html",
        carros=carros,
        resultado=resultado,
        rodada=rodada,
        vez_computador=vez_computador,
        atributo_escolhido=session.get("atributo_escolhido"),
        vencedor_rodada=session.get("vencedor_rodada"),
        vitorias_jogador=vitorias_jogador,
        vitorias_computador=vitorias_computador,
        empates=empates,
        rodada_contabilizada=session["rodada_contabilizada"],
        partida_finalizada=session["partida_finalizada"],
        resultado_final=resultado_final
    )


if __name__ == "__main__":
    app.run(debug=True)
