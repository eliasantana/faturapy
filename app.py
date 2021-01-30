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


@app.route("/", methods=['GET', 'POST'])
def index():
    '''
    sql = "CREATE TABLE teste2 (id INTEGER, TESTE VARCHAR(20))"
    conexao(sql)
    '''
    form = LoginForm()
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '202649'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_DB'] = 'dbfat'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config['SECRET_KEY'] = '3l14ss4nt4n4'
    mysql = MySQL(app)

    app.run(debug=True)
