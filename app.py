# -*- coding: utf-8 -*
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, email
from hashlib import md5
from flask_mail import Mail, Message

app = Flask(__name__)


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class CadastroForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    sobrenome = StringField('sobrenome', validators=[DataRequired()])
    endereco = StringField('endereco', validators=[DataRequired()])
    bairro = StringField('bairro', validators=[DataRequired()])
    cep = StringField('cep', validators=[DataRequired()])
    cidade = StringField('cidade', validators=[DataRequired()])
    uf = SelectField('uf',
                     choices=[('AC'), ('AL'), ('AP'), ('AM'), ('BA'), ('CE'), ('ES'), ('GO'), ('MA'), ('MT'), ('MS'),
                              ('MG'),
                              ('PA'), ('PB'), ('PR'), ('PE'), ('PI'), ('RJ'), ('RN'), ('RS'), ('RO'), ('RR'), ('SC'),
                              ('SP'),
                              ('SE'), ('TO'), ('DF')])
    login = StringField('login', validators=[DataRequired()])
    senha = PasswordField('senha', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])


def conexao(sql):
    con = mysql.connection.cursor()
    con.execute(sql)


def query(sql):
    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    return result


@app.route("/", methods=['GET', 'POST'])
def index():
    form = LoginForm()
    loginform = form.username.data
    passwordform = form.password.data

    if passwordform != None:
        passwordform = geraHashMd5(passwordform)
        print('Senh Informada-> {}  - {} '.format(loginform, passwordform))

    sql = "SELECT login, senha, sn_ativo FROM dbfat.usuario WHERE login = '{}' AND senha = '{}'".format(loginform,
                                                                                                        passwordform)
    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()

    lista = list(result)

    print(lista)

    if loginform == None and passwordform == None:
        erro = ''
    else:
        erro = "Usuário ou senha inválidos!"

    if len(lista) > 0:
        loginDb = result[0]['login']
        passworDb = result[0]['senha']
        ativo = result[0]['sn_ativo']

        if loginDb == loginform and passworDb == passwordform and ativo == 'S':
            return render_template('dashboard.html')
        else:
            return render_template('index.html', form=form, erro=erro)
    else:
        return render_template('index.html', form=form, erro=erro)


@app.route('/cadusuario', methods=['GET', 'POST'])
def cadusuario():
    cadastro = CadastroForm()
    return render_template('cadusuario.html', cadastro=cadastro)


@app.route('/cadastra', methods=['GET', 'POST'])
def cadastrar():
    cadastro = CadastroForm()
    nome = cadastro.nome.data
    sobrenome = cadastro.sobrenome.data
    endereco = cadastro.endereco.data
    bairro = cadastro.bairro.data
    cep = cadastro.cep.data
    cidade = cadastro.cidade.data
    uf = cadastro.uf.data
    snAtivo = 'N'
    snAdministrador = 'N'
    email = cadastro.login.data
    login = cadastro.login.data
    password = cadastro.senha.data
    hashPassword = geraHashMd5(password)
    form = LoginForm()
    erro = ''
    if usuario_existe(login, hashPassword):
        erro = 'Usuário informado já existe!'
        print('USUÁRIO JÁ EXISTE!')

    else:
        cadastra_usuario(nome, sobrenome, endereco, bairro, cep, cidade, uf, login, password, snAtivo, snAdministrador,
                         email)
        print('CADASTRO REALIZADO COM SUCESSO!')
        id = retornaIDuaurio(login, hashPassword)
        enviaEmailAtivacao(nome, id,email)

    return render_template('index.html', form=form, erro=erro)


@app.route('/ativar/<id>',methods=['GET','POST'])
def ativaCadastro(id):
    form = LoginForm()
    erro="Parabéns seu cadastro foi ativado!"
    sql="UPDATE dbfat.usuario SET sn_ativo = 'S' where cd_usuario = {}".format(id)
    conn = mysql.connection.cursor()
    conn.execute(sql)
    mysql.connection.commit()
    return render_template('index.html',form=form, erro=erro)

def geraHashMd5(frase):
    sql = "SELECT MD5('{}') hash FROM DUAL".format(frase)
    c = mysql.connection.cursor()
    c.execute(sql)
    r = c.fetchall()
    return (r[0]['hash'])


@app.route('/email/<usuario>/<idUsuario>', methods=['GET', 'POST'])
def enviaEmailAtivacao(usuario, idUsuario, destinatario):

    msg = Message("Ativação de Conta.", sender='{}'.format(destinatario), recipients=['eliasantana@hotmail.com'])
    msg.html="Caro(a) {}, para ativar sua conta clique [<a href='http://127.0.0.1:5000/ativar/{}'> aqui! </a>]".format(usuario,idUsuario)
    mail.send(msg)
    return 'Email enviado com sucesso!!!!'

def retornaIDuaurio(login, senha):
    sql = "select cd_usuario from dbfat.usuario where senha='{}' and login='{}'".format(senha, login)

    conn = mysql.connection.cursor()
    conn.execute(sql)
    resul = conn.fetchall()

    return resul[0]['cd_usuario']


'''
    VERIFICA A EXISTENCIA DE UM USUÁRIO NA BASE 
'''
def usuario_existe(login, senha):
    sql = "SELECT login, senha, sn_ativo FROM dbfat.usuario WHERE login = '{}' AND senha = '{}'".format(login, senha)
    result = query(sql)
    if len(result) > 0:
        return True
    else:
        return False

@app.route('/dash', methods=['GET'])
def dash():
    return render_template('dashboard.html')


def cadastra_usuario(nome, sobrenome, endereco, bairro, cep, cidade, uf, login, senha, snAtivo, snAdministrador, email):
    sql = "INSERT INTO dbfat.usuario(" \
          "NM_USUARIO," \
          "SOBRE_NOME," \
          "ENDERECO," \
          "BAIRRO," \
          "CEP," \
          "CIDADE," \
          "UF," \
          "LOGIN," \
          "SENHA," \
          "SN_ATIVO," \
          "SN_ADMINISTRADOR," \
          "EMAIL," \
          "DT_CADASTRO) " \
          "VALUES('{}','{}','{}','{}','{}','{}','{}','{}',md5('{}'),'{}','{}','{}',current_timestamp())" \
        .format(nome, sobrenome, endereco, bairro, cep, cidade, uf, login, senha, snAtivo, snAdministrador, email)

    mysql.connection.query(sql)
    mysql.connection.commit()


if __name__ == '__main__':
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '202649'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_DB'] = 'dbfat'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config['SECRET_KEY'] = '3l14ss4nt4n4'

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'eliasantanasilva@gmail.com'
    app.config['MAIL_PASSWORD'] = 'iiewbgoyzlumnqvm'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    mysql = MySQL(app)
    mail = Mail()
    mail.init_app(app)

    app.run(debug=True)
