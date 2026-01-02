from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # <<< ESSENCIAL


# -------------------------
# GABARITO
# -------------------------
GABARITO = {
    1: "B",  # Garantir registros operacionais rastreáveis e padronizados
    2: "A",  # Verdadeiro
    3: "B",  # Passagem de serviço entre turnos
    4: "B",  # Colaboradores em serviço e líderes de turno
    5: "V",  # Verdadeiro
    6: "B",  # Falhas na continuidade do serviço
    7: "B",  # Aguardar a sincronização completa do aplicativo
    8: "F",  # Falso
    9: "C",  # Não compartilhar usuário e senha
    10: "C", # Anotações
    11: "V", # Verdadeiro
    12: "B", # Registrar no Livro Ata Digital e comunicar supervisor
    13: "B", # Registrar retirada e devolução
    14: "F", # Falso
    15: "C", # Acionar supervisão
}
EXPLICACOES = {
    1: "O Livro Ata Digital garante registros rastreáveis e padronizados.",
    2: "A afirmação apresentada é verdadeira conforme o procedimento.",
    3: "A passagem de serviço deve ocorrer entre turnos.",
    4: "A responsabilidade envolve colaboradores em serviço e líderes.",
    5: "A afirmativa é verdadeira conforme norma interna.",
    6: "A alternativa correta trata falhas na continuidade do serviço.",
    7: "É necessário aguardar a sincronização completa do aplicativo.",
    8: "A afirmativa apresentada é falsa.",
    9: "Nunca se deve compartilhar usuário e senha.",
    10: "O Livro Ata registra anotações operacionais.",
    11: "A afirmativa é verdadeira.",
    12: "O correto é registrar no Livro Ata Digital e comunicar o supervisor.",
    13: "Toda retirada e devolução deve ser registrada.",
    14: "A afirmativa é falsa.",
    15: "A supervisão deve ser acionada."
}

SECOES_NOMES = {
    1: "Objetivo e Finalidade do Livro Ata Digital",
    2: "Responsabilidades e Consequências",
    3: "Acesso ao Sistema e Confirmações",
    4: "Funcionalidades do Livro Ata Digital",
    5: "Procedimentos e Boas Práticas"
}


# -------------------------
# CONFIGURAÇÕES
# -------------------------
app = Flask(__name__)
app.secret_key = "brasfort_pro"
DB_NAME = "database.db"

# -------------------------
# FUNÇÃO DE CONEXÃO
# -------------------------
def conectar():
    return sqlite3.connect(DB_NAME)

# -------------------------
# CRIAÇÃO DO BANCO
# -------------------------
def criar_banco():
    conn = conectar()
    c = conn.cursor()

    # apaga tabelas antigas
    c.execute("DROP TABLE IF EXISTS login")
    c.execute("DROP TABLE IF EXISTS avaliacoes")

    # cria tabela login
    c.execute("""
    CREATE TABLE login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        matricula TEXT,
        posto TEXT,
        data_login TEXT,
        hora_login TEXT
    )
    """)

    # -------------------------
# CRIAÇÃO DO BANCO
# -------------------------
def criar_banco():
    conn = conectar()
    c = conn.cursor()

    # cria tabela login se não existir
    c.execute("""
    CREATE TABLE IF NOT EXISTS login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        matricula TEXT,
        posto TEXT,
        data_login TEXT,
        hora_login TEXT
    )
    """)

    # cria tabela avaliacoes se não existir
    c.execute("""
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_avaliacao TEXT,
        hora_avaliacao TEXT,
        tempo_formatado TEXT,
        matricula TEXT,
        nome TEXT,
        posto TEXT,
        status TEXT,
        nota_geral REAL,
        nota_secao_1 REAL,
        nota_secao_2 REAL,
        nota_secao_3 REAL,
        nota_secao_4 REAL,
        nota_secao_5 REAL,
        q1_resposta TEXT,
        q2_resposta TEXT,
        q3_resposta TEXT,
        q4_resposta TEXT,
        q5_resposta TEXT,
        q6_resposta TEXT,
        q7_resposta TEXT,
        q8_resposta TEXT,
        q9_resposta TEXT,
        q10_resposta TEXT,
        q11_resposta TEXT,
        q12_resposta TEXT,
        q13_resposta TEXT,
        q14_resposta TEXT,
        q15_resposta TEXT
    )
    """)

    conn.commit()
    conn.close()


# -------------------------
# ROTA DE LOGIN
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        matricula = request.form["matricula"].strip()
        posto = request.form["posto"].strip()

        agora = datetime.now()
        data = agora.strftime("%d/%m/%Y")
        hora = agora.strftime("%H:%M:%S")

        conn = conectar()
        c = conn.cursor()
        c.execute("""
            INSERT INTO login (nome, matricula, posto, data_login, hora_login)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, matricula, posto, data, hora))
        conn.commit()
        conn.close()

        session["nome"] = nome
        session["matricula"] = matricula
        session["posto"] = posto

        return redirect("/documentacao")

    return render_template("login.html")

# -------------------------
# ROTA DOCUMENTAÇÃO
# -------------------------
@app.route("/documentacao")
def documentacao():
    return render_template("documentacao.html")

@app.route("/painel-avaliacoes")
def painel_avaliacoes():
    return render_template("painel-avaliacoes.html")

# -------------------------
# ROTA AVALIAÇÃO
# -------------------------
@app.route("/avaliacao", methods=["GET", "POST"])
def avaliacao():

    # ---------- GET ----------
    if request.method == "GET":
        session["inicio_avaliacao"] = datetime.now().isoformat()
        return render_template("avaliacao.html")

    # ---------- POST ----------
    inicio = datetime.fromisoformat(session["inicio_avaliacao"])
    fim = datetime.now()

    tempo_segundos = int((fim - inicio).total_seconds())
    minutos = tempo_segundos // 60
    segundos = tempo_segundos % 60
    tempo_formatado = f"{minutos:02d}:{segundos:02d}"

    respostas_texto = []
    respostas_acerto = []

    for i in range(1, 16):
        resposta = request.form.get(f"q{i}", "").strip().upper()
        respostas_texto.append(resposta)

        acerto = 1 if resposta == GABARITO[i] else 0
        respostas_acerto.append(acerto)
    questoes_detalhadas = []

    for i in range(1, 16):
        marcada = respostas_texto[i-1]
        correta = GABARITO[i]

        questoes_detalhadas.append({
            "numero": i,
            "marcada": marcada,
            "correta": correta,
            "acertou": marcada == correta,
            "explicacao": EXPLICACOES.get(i, "")
        })

    # ---------- NOTAS ----------
    nota_geral = round(sum(respostas_acerto) / 15 * 100, 2)
    secoes = [
        round(sum(respostas_acerto[i:i+3]) / 3 * 100, 2)
        for i in range(0, 15, 3)
    ]

    status = "Habilitado" if nota_geral >= 90 else "Não Habilitado"

    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")

    # ---------- SALVAR NO BANCO ----------
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO avaliacoes (
            data_avaliacao, hora_avaliacao, tempo_formatado,
            matricula, nome, posto, status, nota_geral,
            nota_secao_1, nota_secao_2, nota_secao_3, nota_secao_4, nota_secao_5,
            q1_resposta, q2_resposta, q3_resposta, q4_resposta, q5_resposta,
            q6_resposta, q7_resposta, q8_resposta, q9_resposta, q10_resposta,
            q11_resposta, q12_resposta, q13_resposta, q14_resposta, q15_resposta
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data, hora, tempo_formatado,
        session["matricula"], session["nome"], session["posto"],
        status, nota_geral,
        *secoes,
        *respostas_texto
    ))
    conn.commit()
    conn.close()

    # ---------- DECISÃO DE TELA ----------
    template = (
        "resultado_habilitado.html"
        if nota_geral >= 90
        else "resultado_nao_habilitado.html"
    )

    return render_template(
        template,
        nome=session["nome"],
        matricula=session["matricula"],
        posto=session["posto"],
        status=status,
        nota=nota_geral,
        secoes=secoes,
        secoes_nomes=SECOES_NOMES,
        tempo=tempo_formatado,
        questoes=questoes_detalhadas
    )
# -------------------------
# API PARA BI
# -------------------------
@app.route("/api/avaliacoes")
def api_avaliacoes():
    conn = conectar()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM avaliacoes")
    dados = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(dados)

@app.route("/api/login")
def api_login():
    conn = conectar()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM login")
    dados = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(dados)

# -------------------------
# RODAR O APP
# -------------------------
if __name__ == "__main__":
    criar_banco()  # agora apenas garante que as tabelas existam
    app.run(debug=True, port=5001)

