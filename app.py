# -*- coding: utf-8 -*
from flask import Flask, render_template, jsonify, session, request, redirect, url_for, json
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from jinja2.filters import do_trim
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, SelectField, FloatField, IntegerField, DateField
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
    ds_lancamento = StringField('ds_lancamento', validators=[DataRequired()])
    vl_previsto = FloatField('vl_previsto', validators=[DataRequired()])
    vl_realizado = FloatField('vl_realizado', validators=[DataRequired()])
    parcela = IntegerField('parcela', validators=[DataRequired()])
    dt_vencimento = DateField('parcela', validators=[DataRequired()])
    dt_pagamento = DateField('parcela', validators=[DataRequired()])
    tp_lancamento = SelectField('tp_lancamento', choices=[('D', 'Despesa'), ('R', 'Receita')])
    cd_usuario = IntegerField('parcela', validators=[DataRequired()])


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
    sql = "SELECT CD_USUARIO FROM DBFAT.USUARIO WHERE LOGIN = '{}'".format(login)
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
        # print('Senh Informada-> {}  - {} '.format(loginform, passwordform))

    sql = "SELECT cd_usuario, login, senha, sn_ativo FROM dbfat.usuario WHERE login = '{}' AND senha = '{}'".format(
        loginform,
        passwordform)
    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()

    lista = list(result)

    #print(lista)

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
            lcto = retorna_lancamento_ano_atual(idusuario)
            resumo = resumo_mensal(idusuario)

            valores = list()
            ''' Separa meses e valores em listas diferentes '''
            meses = ""
            valor_str = ""
            lista = ['0','0','0','0','0','0','0','0','0','0','0','0','0']

            for i in range(len(resumo)):
                mes = str((resumo[i]['mes']))
                valor = str((resumo[i]['total']))
                if mes == 'Jan':
                    lista[0]=valor
                elif mes =='Fev':
                    lista[1]=valor
                elif mes =='Mar':
                    lista[2]=valor
                elif mes == 'Abr':
                    lista[3]=valor
                elif mes == 'Mai':
                    lista[4]=valor
                elif mes == 'Jun':
                    lista[5]=valor
                elif mes == 'Jul':
                    lista[6]=valor
                if mes == 'Ago':
                    lista[7]=valor
                elif mes =='Set':
                    lista[8]=valor
                elif mes =='Out':
                    lista[9]=valor
                elif mes == 'Nov':
                    lista[10]=valor
                elif mes == 'Dez':
                    lista[11]=valor


            valores = ",".join(lista)
            # Index
            return render_template('dashboard.html', loginform=loginform, lcto=lcto, data=data, idusuario=idusuario, meses=meses, valores=valores)
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
        enviaEmailAtivacao(nome, id, email)

    return render_template('index.html', form=form, erro=erro)


@app.route('/ativar/<id>', methods=['GET', 'POST'])
def ativaCadastro(id):
    form = LoginForm()
    erro = "Parabéns seu cadastro foi ativado!"
    sql = "UPDATE dbfat.usuario SET sn_ativo = 'S' where cd_usuario = {}".format(id)
    conn = mysql.connection.cursor()
    conn.execute(sql)
    mysql.connection.commit()
    return render_template('index.html', form=form, erro=erro)


def geraHashMd5(frase):
    sql = "SELECT MD5('{}') hash FROM DUAL".format(frase)
    c = mysql.connection.cursor()
    c.execute(sql)
    r = c.fetchall()
    return (r[0]['hash'])


@app.route('/email/<usuario>/<idUsuario>', methods=['GET', 'POST'])
def enviaEmailAtivacao(usuario, idUsuario, destinatario):
    msg = Message("Ativação de Conta.", sender='{}'.format(destinatario), recipients=['eliasantana@hotmail.com'])
    msg.html = "Caro(a) {}, para ativar sua conta clique [<a href='http://127.0.0.1:5000/ativar/{}'> aqui! </a>]".format(
        usuario, idUsuario)
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

    form.tp_lancamento.data = lista[0]['tp_lancamento']
    form.ds_lancamento.data = lista[0]['ds_lancamento']
    form.parcela.data = lista[0]['parcela']
    form.vl_previsto.data = lista[0]['vl_previsto']
    form.vl_realizado.data = lista[0]['vl_realizado']
    form.dt_vencimento.data = datetime.strptime(lista[0]['dt_vencimento'], "%d/%m/%Y")

    ds_lancamento = form.ds_lancamento.data
    vl_previsto = form.vl_previsto.data
    vl_realizado = form.vl_realizado.data
    parcela = form.parcela.data
    dt_vencimento = form.dt_vencimento.data
    tp_lancamento = form.tp_lancamento.data
    print(vl_previsto)

    # return render_template('lancamentos.html', form=form, idusuario=idusuario)
    return render_template('lancamentos_editar.html', form=form, idusuario=idusuario)


@app.route('/alterar', methods=['POST'])
def alterarDados():
    form = Lancamento()
    ds_lancamento = form.ds_lancamento.data
    vl_previsto = form.vl_previsto.data
    vl_realizado = form.vl_realizado.data
    parcela = form.parcela.data
    dt_vencimento = request.form['calendario']
    dt_vencimento = datetime.strptime(dt_vencimento, "%d/%m/%Y")
    tp_lancamento = form.tp_lancamento.data
    idusuario = session['idUsuario']
    idLancamento = session['idlancamento']

    sql = "UPDATE DBFAT.LANCAMENTOS SET ds_lancamento='{}', " \
          "vl_previsto={}, vl_realizado={}, parcela={}, " \
          "dt_vencimento='{}', tp_lancamento='{}' " \
          "WHERE CD_USUARIO='{}' AND CD_LANCAMENTO={}".format(ds_lancamento, vl_previsto, vl_realizado, parcela,
                                                              dt_vencimento, tp_lancamento, idusuario,
                                                              idLancamento)
    print(sql)
    mysql.connection.query(sql)
    mysql.connection.commit()

    lista = retorna_lista_lancamentos(idusuario)

    return render_template('lancamentos.html', form=form, lista=lista, idusuario=idusuario)


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
          "cd_usuario, date_format(dt_vencimento,'%d/%m/%Y') dt_vencimento from dbfat.lancamentos where CD_lancamento = {}".format(
        idlancamento)

    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    lista = list(result)

    return lista


@app.route('/dash', methods=['GET'])
def dash():
    form = LoginForm()
    data = datetime.now()
    data = data.strftime("%d/%m/%Y")
    idusuario = session['idUsuario']

    ''' Resumo mensal das despesas '''
    resumo = resumo_mensal(idusuario)
    ''' Separa meses e valores em listas diferentes '''
    meses = ""
    valor_str = ""
    lista = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']

    for i in range(len(resumo)):
        mes = str((resumo[i]['mes']))
        valor = str((resumo[i]['total']))
        if mes == 'Jan':
            lista[0] = valor
        elif mes == 'Fev':
            lista[1] = valor
        elif mes == 'Mar':
            lista[2] = valor
        elif mes == 'Abr':
            lista[3] = valor
        elif mes == 'Mai':
            lista[4] = valor
        elif mes == 'Jun':
            lista[5] = valor
        elif mes == 'Jul':
            lista[6] = valor
        if mes == 'Ago':
            lista[7] = valor
        elif mes == 'Set':
            lista[8] = valor
        elif mes == 'Out':
            lista[9] = valor
        elif mes == 'Nov':
            lista[10] = valor
        elif mes == 'Dez':
            lista[11] = valor

    valores = ",".join(lista)

    lcto = retorna_lancamento_ano_atual(idusuario)
    #aqui
    return render_template('dashboard.html', form=form, lcto=lcto, data=data, idusuario=idusuario, meses=meses,valores=valores)
    #return render_template('dashboard.html', loginform=loginform, lcto=lcto, data=data, idusuario=idusuario, meses=meses, valores=valores)

@app.route('/lancamento/<int:idusuario>', methods=['GET', 'POST'])
def exibelancamento(idusuario):
    form = Lancamento()
    lista = retorna_lista_lancamentos(idusuario)
    return render_template('lancamentos.html', form=form, lista=lista, idusuario=idusuario)


def retorna_lista_lancamentos(idusuario):
    '''
    Desde:03-03-2021
    Autor: Elias Santana
    Retorna uma a lista de lançamentos do mês atual
    '''
    sql = "SELECT  ds_lancamento, format(vl_previsto,2,'de_DE') vl_previsto, " \
          "format(vl_realizado,2,'de_DE') vl_realizado, " \
          "parcela, " \
          "dt_vencimento, " \
          "tp_lancamento, " \
          "CD_USUARIO,  " \
          "CD_LANCAMENTO FROM DBFAT.LANCAMENTOS WHERE CD_USUARIO = {} " \
          "AND date_format(dt_vencimento,'%m') = date_format(curdate(),'%m')".format(idusuario)

    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    lista = list(result)
    print(lista)
    return lista


def retorna_lancamento_ano_atual(cd_usuario):
    '''
        Retorna os lancamentos por usuário no ano corrente agrupados por data de pagamento
    '''
    sql = "SELECT " \
          "ds_lancamento, " \
          "format(vl_previsto,2,'de_DE') 'previsto', " \
          "format(vl_realizado,2,'de_DE') 'realizado', " \
          "parcela, date_format(dt_vencimento,'%d/%m/%Y') 'vencimento', " \
          "date_format(dt_pagamento,'%d/%m/%Y') 'pago', " \
          "case when tp_lancamento = 'D' then " \
          "'Despesa' " \
          "else 'Receita' " \
          "end as 'lancamento'" \
          "FROM dbfat.lancamentos " \
          "where cd_usuario = {} and date_format(dt_pagamento,'Y') = date_format(curdate(),'Y') " \
          "order by dt_pagamento".format(cd_usuario)

    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    lista = list(result)
    return lista

def resumo_mensal(id_usuario):
    sql= "select case when date_format(dt_pagamento, '%m') = 1 then 'Jan' when date_format(dt_pagamento, '%m') = 2 then 'Fev' when date_format(dt_pagamento, '%m') = 3 then 'Mar' when date_format(dt_pagamento, '%m') = 4 then 'Abr' when date_format(dt_pagamento, '%m') = 5 then 'Mai' when date_format(dt_pagamento, '%m') = 6 then 'Jun' when date_format(dt_pagamento, '%m') = 7 then 'Jul' when date_format(dt_pagamento, '%m') = 8 then 'Ago' when date_format(dt_pagamento, '%m') = 9 then 'Set' when date_format(dt_pagamento, '%m') = 10 then 'Out' when date_format(dt_pagamento, '%m') = 11 then 'Nov' when date_format(dt_pagamento, '%m') = 12 then 'Dez' else date_format(dt_pagamento, '%m') end as mes, sum(vl_realizado) total from dbfat.lancamentos where CD_USUARIO = {} and date_format(dt_pagamento,'Y') = date_format(curdate(),'Y') group by date_format(dt_pagamento,'%m')".format(id_usuario)
    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    resumo = list(result)

    return resumo

@app.route('/excluilancamento/<int:idlancamento>', methods=['GET', 'POST'])
def excluir(idlancamento):
    '''
        Excluir um vencimento
    '''
    form = Lancamento()
    sql = "DELETE FROM DBFAT.LANCAMENTOS WHERE CD_LANCAMENTO = {}".format(idlancamento)
    mysql.connection.query(sql)
    mysql.connection.commit()
    idusuario = session['idUsuario']
    print('Sessão: {}'.format(idusuario))
    lista = retorna_lista_lancamentos(idusuario)
    return render_template('lancamentos.html', form=form, idusuario=idusuario, lista=lista)


@app.route('/adiciona/<int:idusuario>', methods=['GET', 'POST'])
def adicionar_lancamento(idusuario):
    '''
        Adiciona ou altera um lancamento
    '''
    form = Lancamento()
    ds_lancamento = form.ds_lancamento.data
    vl_previsto = form.vl_previsto.data
    vl_realizado = form.vl_realizado.data
    parcela = form.parcela.data
    dt_vencimento = request.form['calendario']
    dt_vencimeSnto = datetime.strptime(dt_vencimento, "%d/%m/%Y").date()
    print(dt_vencimeSnto)
    tp_lancamento = form.tp_lancamento.data
    cd_usuario = form.cd_usuario.data
    #print(dt_vencimento)
    #id_lancamento = session['idlancamento']
    sql = "INSERT INTO DBFAT.LANCAMENTOS (ds_lancamento, vl_previsto, vl_realizado, parcela, dt_vencimento, tp_lancamento, CD_USUARIO) VALUES ('{}',{},{},{},'{}','{}',{})".format(ds_lancamento, vl_previsto, vl_realizado, parcela, dt_vencimeSnto, tp_lancamento, idusuario)
    print(sql)
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

@app.route('/teste',methods=['GET','POST'])
def teste():
    resumo = resumo_mensal(26)
    meses =""
    for i in range(len(resumo)):
        mes = str(resumo[i]['mes'])
        meses = meses + mes+","
    return meses


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

