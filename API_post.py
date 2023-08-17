from flask import Flask, jsonify, request, make_response
from datetime import datetime, timedelta
from estrutura_db import Autor, Postagem, app, db
from functools import wraps
import jwt
import os


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem': 'Token não foi incluído!'}, 401)
        # Se temos um token, validar acesso consultando o BD
        try:
            resultado = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(
                id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'Token inválido'}, 401)
        return f(autor, *args, **kwargs)
    return decorated


@app.route('/cadastro', methods=['POST'])
def cadastro():
    novo_usuario = request.get_json()
    if 'nome' not in novo_usuario or 'email' not in novo_usuario or 'senha' not in novo_usuario:
        return jsonify({'mensagem': 'Campos obrigatórios não fornecidos.'}, 400)
    if Autor.query.filter_by(email=novo_usuario['email']).first():
        return jsonify({'mensagem': 'Este email já está em uso.'}, 400)
    autor = Autor(
        nome=novo_usuario['nome'],
        email=novo_usuario['email'],
        senha=novo_usuario['senha'],
        admin=False
    )
    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado com sucesso!'}, 200)


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow(
        ) + timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token})

    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})


@app.route('/')
@token_obrigatorio
def obter_postagens(autor):
    postagens = Postagem.query.all()
    lista_de_postagens = []  # <?>
    for postagem in postagens:
        postagem_atual = {}  # <?>
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        lista_de_postagens.append(postagem_atual)

        return jsonify({'lista de postagens': postagem_atual})


# Obter postagem por id - GET http:///localhost:5000/postagem/1


@app.route('/postagem/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_indice(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    postagem_atual = {}  # <?>
    try:
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass
    try:
        postagem_atual['id_autor'] = postagem.id_autor
    except:
        pass

    return jsonify({'postagens': postagem_atual})

# Criar uma nova postagem - POST http://localhost:5000/postagem


@app.route('/postagem', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()  # <?>
    postagem = Postagem(
        titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])

    db.session.add(postagem)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem criada com sucesso.'})

# Alterar uma postagem existente - PUT http://localhost:5000/postagem/1


@app.route('/postagem/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(
        id_postagem=id_postagem).first()
    try:
        postagem.titulo = postagem_alterada['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_alterada['id_autor']
    except:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Postagem alterada com sucesso.'})


@app.route('/postagem/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def apagar_postagem(autor, id_postagem):
    postagem_a_ser_excluida = Postagem.query.filter_by(
        id_postagem=id_postagem).first()
    if not postagem_a_ser_excluida:
        return jsonify({'mensagem': 'Não foi encontrada a postagem com este ID!'})
    db.session.delete(postagem_a_ser_excluida)
    db.session.commit()

    return jsonify({'mensagem': 'A postagem foi excluída com sucesso.'})


@app.route('/autores')
@token_obrigatorio
def obter_autores(autor):
    # Extrair todos os dados que estão dentro da respectiva tabela
    autores = Autor.query.all()
    lista_de_autores = []  # Será utilizada abaixo
    for autor in autores:
        autor_atual = {}  # Dicionário vazio que será adicionado a lista
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        autor_atual['admin'] = autor.admin
        lista_de_autores.append(autor_atual)

    return jsonify({'autores': lista_de_autores})


@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_por_id(autor, id_autor):
    # Queremos apenas o primeiro resultado, por isso o uso da função first()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not Autor:
        return jsonify('Autor não encontrado!')

    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    autor_atual['admin'] = autor.admin

    return jsonify({'autor': autor_atual})


@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(
        nome=novo_autor['nome'], senha=novo_autor['senha'], email=novo_autor['email'])

    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado com sucesso!'}, 200)


@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor, id_autor):
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not Autor:
        return jsonify({'mensagem': 'Usuário não encontrado!'})
    try:
        autor.nome = usuario_a_alterar['nome']
    except:
        pass
    try:
        autor.email = usuario_a_alterar['email']
    except:
        pass
    try:
        autor.senha = usuario_a_alterar['senha']
    except:
        pass

    db.session.commit()

    return jsonify({'mensagem': 'Usuário alterado com sucesso!'})


@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    autor_existente = Autor.query.filter_by(
        id_autor=id_autor).first()  # -> Busca apenas o primeiro
    if not autor_existente:
        return jsonify({'mensagem': 'Este autor não foi encontrado.'})

    db.session.delete(autor_existente)
    db.session.commit()

    return jsonify({'mensagem': 'Autor excluído com sucesso!'})

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT', default=5000))
