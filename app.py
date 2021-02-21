# -*- coding: utf-8 -*
from flask import Flask, render_template, jsonify, session, request, redirect, url_for
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from jinja2.filters import do_trim
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, SelectField,FloatField, IntegerField, DateField
from wtforms.validators import DataRequired, email
from flask_mail import Mail, Message
from datetime import datetime

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

class Lancamento(FlaskForm):

     ds_lancamento=StringField('ds_lancamento', validators=[DataRequired()])
     vl_previsto=FloatField('vl_previsto', validators=[DataRequired()])
     vl_realizado=FloatField('vl_realizado', validators=[DataRequired()])
     parcela=IntegerField('parcela', validators=[DataRequired()])
     dt_vencimento=DateField('parcela', validators=[DataRequired()])
     dt_pagamento=DateField('parcela', validators=[DataRequired()])
     tp_lancamento=SelectField('tp_lancamento', choices=[('D','Despesa'),('R','Receita')])
     cd_usuario=IntegerField('parcela', validators=[DataRequired()])

def conexao(sql):
    con = mysql.connection.cursor()
    con.execute(sql)

def existe_lancamento(idlancamento):
    sql = 'SELECT 1 CD_LANCAMENTO  FROM dbfat.lancamentos WHERE CD_LANCAMENTO ={}'.format(idlancamento)
    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    lista = list(result)
    if len(lista) > 0:
        return True
    else:
        return False


def query(sql):
    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    return result


def retornaIDusuarioLogado(login):
    sql="SELECT CD_USUARIO FROM DBFAT.USUARIO WHERE LOGIN = '{}'".format(login)
    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    lista = list(result)

    return lista[0]['CD_USUARIO']



@app.route("/", methods=['GET', 'POST'])
def index():
    form = LoginForm()
    loginform = form.username.data
    passwordform = form.password.data
    data = datetime.now()
    data = data.strftime("%d/%m/%Y")
    if passwordform != None:
        passwordform = geraHashMd5(passwordform)
        #print('Senh Informada-> {}  - {} '.format(loginform, passwordform))

    sql = "SELECT cd_usuario, login, senha, sn_ativo FROM dbfat.usuario WHERE login = '{}' AND senha = '{}'".format(loginform,
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
        idusuario = retornaIDusuarioLogado(loginDb)
        session['idUsuario'] = idusuario
        if loginDb == loginform and passworDb == passwordform and ativo == 'S':
            return render_template('dashboard.html', loginform = loginform, data = data, idusuario=idusuario)
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


def lista_lancamentos(idusuario):
    sql = "SELECT  ds_lancamento, format(vl_previsto,2,'de_DE') vl_previsto, " \
          "format(vl_realizado,2,'de_DE') vl_realizado, " \
          "parcela, " \
          "dt_vencimento, " \
          "tp_lancamento, " \
          "CD_USUARIO  " \
          "FROM DBFAT.LANCAMENTOS WHERE CD_USUARIO = {}".format(idusuario)

    result = query(sql)
    lista = list(result)
    return lista

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

@app.route('/editar/<int:idlancamento>')
def edita_lancamento(idlancamento):
    '''
    Retorna retorna o formulário com os dados carregados.
    '''
    lista = localiza_lancametno(idlancamento)
    form = Lancamento()
    print(lista)

    idusuario = session['idUsuario']
    session['idlancamento'] = lista[0]['cd_lancamento']
    form.ds_lancamento.data= lista[0]['ds_lancamento']
    form.parcela.data = lista[0]['parcela']
    form.vl_previsto.data = lista[0]['vl_previsto']
    form.vl_realizado.data = lista[0]['vl_realizado']
    form.dt_vencimento.data = lista[0]['dt_vencimento']

    return render_template('lancamentos.html', form=form, idusuario=idusuario)


def localiza_lancametno(idlancamento):
    '''
    Localiza um lançamento filtrando pelo cd_lancamento
    '''
    sql = "select cd_lancamento, " \
          "ds_lancamento, " \
          "vl_previsto, " \
          "vl_realizado, " \
          "parcela, " \
          "tp_lancamento, " \
          "cd_usuario, dt_vencimento from dbfat.lancamentos where CD_lancamento = {}".format(idlancamento)

    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    lista = list(result)

    return lista

@app.route('/dash', methods=['GET'])
def dash():
    idusuario = session['idUsuario']
    return render_template('dashboard.html',idusuario=idusuario)


@app.route('/lancamento/<int:idusuario>', methods=['GET','POST'])
def exibelancamento(idusuario):
    form = Lancamento()
    lista  = retorna_lista_lancamentos(idusuario)
    return render_template('lancamentos.html',form=form, lista=lista, idusuario=idusuario)

def retorna_lista_lancamentos(idusuario):
    '''
    Retorna uma a lista de lançamentos
    '''
    sql = "SELECT  ds_lancamento, format(vl_previsto,2,'de_DE') vl_previsto, " \
          "format(vl_realizado,2,'de_DE') vl_realizado, " \
          "parcela, " \
          "dt_vencimento, " \
          "tp_lancamento, " \
          "CD_USUARIO,  " \
          "CD_LANCAMENTO FROM DBFAT.LANCAMENTOS WHERE CD_USUARIO = {}".format(idusuario)

    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    lista = list(result)
    print(lista)
    return lista


@app.route('/excluilancamento/<int:idlancamento>',methods=['GET','POST'])
def excluir(idlancamento):
    '''
        Excluir um vencimento
    '''
    form = Lancamento()
    sql="DELETE FROM DBFAT.LANCAMENTOS WHERE CD_LANCAMENTO = {}".format(idlancamento)
    mysql.connection.query(sql)
    mysql.connection.commit()
    idusuario = session['idUsuario']
    print('Sessão: {}'.format(idusuario))
    lista = retorna_lista_lancamentos(idusuario)
    return render_template('lancamentos.html',form=form,idusuario=idusuario, lista=lista)


@app.route('/adiciona/<int:idusuario>',methods=['GET','POST'])
def adicionar_lancamento(idusuario):
    '''
        Adiciona e retorna uma lista de lançamentos
    '''
    form = Lancamento()
    ds_lancamento = form.ds_lancamento.data
    vl_previsto = form.vl_previsto.data
    vl_realizado = form.vl_realizado.data
    parcela= form.parcela.data
    dt_vencimento = request.form['calendario']
    tp_lancamento = form.tp_lancamento.data
    cd_usuario = form.cd_usuario.data
    dt_vencimento = datetime.strptime(dt_vencimento,"%d/%m/%Y")
    
    sql="INSERT INTO DBFAT.LANCAMENTOS (ds_lancamento, vl_previsto, vl_realizado, parcela, dt_vencimento, tp_lancamento, CD_USUARIO) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ds_lancamento, vl_previsto, vl_realizado, parcela, dt_vencimento, tp_lancamento, idusuario)
    mysql.connection.query(sql)
    mysql.connection.commit()

    lista = retorna_lista_lancamentos(idusuario)
    return render_template('lancamentos.html', form=form, idusuario=idusuario, lista=lista)

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

