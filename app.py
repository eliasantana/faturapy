# -*- coding: utf-8 -*
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, email

app = Flask(__name__)


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class CadastroForm (FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    sobrenome = StringField('sobrenome', validators=[DataRequired()])
    endereco = StringField('endereco', validators=[DataRequired()])
    bairro = StringField('bairro', validators=[DataRequired()])
    cep = StringField('cep', validators=[DataRequired()])
    cidade = StringField('cidade', validators=[DataRequired()])
    uf = SelectField('uf', choices=[('AC'),('AL'),('AP'),('AM'),('BA'),('CE'),('ES'),('GO'),('MA'),('MT'),('MS'),('MG'),
                                    ('PA'),('PB'),('PR'),('PE'),('PI'),('RJ'),('RN'),('RS'),('RO'),('RR'),('SC'),('SP'),
                                    ('SE'),('TO'),('DF')])
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

    sql = "SELECT login, senha FROM dbfat.usuario WHERE login = '{}' AND senha = '{}'".format(loginform, passwordform)
    result = query(sql)
    lista = list(result)

    if loginform == None and passwordform == None:
        erro = ''
    else:
        erro = "Usuário ou senha inválidos!"

    if len(lista) > 0:
        loginDb = result[0]['login']
        passworDb = result[0]['senha']

        if loginDb == loginform and passworDb == passwordform:
            return render_template('cadusuario.html')
        else:
            return render_template('index.html', form=form, erro=erro)
    else:
        return render_template('index.html', form=form, erro=erro)

@app.route('/cadusuario', methods=['GET', 'POST'])
def cadusuario():
    cadastro = CadastroForm()
    return render_template('cadusuario.html',cadastro=cadastro)

@app.route('/cadastra', methods=['GET','POST'])
def cadastrar ():
    cadastro = CadastroForm()
    nome = cadastro.nome.data
    sobrenome = cadastro.sobrenome.data
    endereco = cadastro.endereco.data
    bairro = cadastro.bairro.data
    cep = cadastro.cep.data
    cidade = cadastro.cidade.data
    uf = cadastro.uf.data
    snAtivo = 'S'
    snAdministrador = 'N'
    email = cadastro.login.data
    login = email
    password = cadastro.senha.data


    if usuario_existe(login, password):
        print('USUÁRIO JÁ EXISTE!')
    else:
        print('executar a pós ferificacao')
        cadastra_usuario(nome, sobrenome, endereco,bairro,cep,cidade,uf,login, password, snAtivo, snAdministrador, email)

    return render_template('cadusuario.html',cadastro=cadastro)


def usuario_existe(login, senha):
    sql = "SELECT login, senha FROM dbfat.usuario WHERE login = '{}' AND senha = '{}'".format(login, senha)
    result = query(sql)
    if len(result) >0:
        return True
    else:
        return False

def cadastra_usuario(nome, sobrenome, endereco, bairro, cep, cidade, uf, login, senha, snAtivo, snAdministrador, email):
    sql="INSERT INTO dbfat.usuario(" \
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
        "VALUES('{}','{}','{}','{}','{}','{}','{}','{}','md5({})','{}','{}','{}',current_timestamp())"\
        .format(nome, sobrenome, endereco,bairro,cep,cidade,uf,login,senha, snAtivo, snAdministrador,email)

    mysql.connection.query(sql)
    mysql.connection.commit()



if __name__ == '__main__':
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '202649'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_DB'] = 'dbfat'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config['SECRET_KEY'] = '3l14ss4nt4n4'
    mysql = MySQL(app)

    app.run(debug=True)
