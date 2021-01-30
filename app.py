# -*- coding: utf-8 -*
from flask import Flask, render_template
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__)


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


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


if __name__ == '__main__':
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '202649'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_DB'] = 'dbfat'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config['SECRET_KEY'] = '3l14ss4nt4n4'
    mysql = MySQL(app)

    app.run(debug=True)
