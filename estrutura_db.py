from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Criar uma API flask

app = Flask(__name__)

# Criando uma instância de SQLALchemy

app.config['SECRET_KEY'] = 'FHC1995'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:iVRarxea5eBiVkDlrMDf@containers-us-west-86.railway.app:7303/railway'
db = SQLAlchemy(app)
db: SQLAlchemy


class Postagem(db.Model):
    __tablename__ = 'postagem'
    # A coluna terá um valor único e que não deve se repetir
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    # ForeignKey -> Estamso referenciando uma outra tbela.
    id_autor = db.Column(db.Integer, db.ForeignKey(
        'autor.id_autor'))  # Nome da tabela


class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem')  # Nome da classe


# Agora vamos garantir que as operações ocorram dentro do contexto da aplicação
def inicializar_banco():
    with app.app_context():
        # Drop e criação das tabelas
        db.drop_all()
        db.create_all()

        # Criar usuários administradores
        autor = Autor(nome='gabriel', email='gabriel@gmail.com',
                      senha='2525', admin=True)
        db.session.add(autor)
        db.session.commit()


if __name__ == '__main__':
    inicializar_banco()
