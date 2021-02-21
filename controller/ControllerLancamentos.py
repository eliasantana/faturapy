from flask_mysqldb import MySQL
from faturapy.app import app



def retornaLancamento(idLacamento):
    sql = "select cd_lancamento, " \
          "ds_lancamento, " \
          "vl_previsto, " \
          "vl_realizado, " \
          "parcela, " \
          "tp_lancamento, " \
          "cd_usuario from dbfat.lancamentos where CD_lancamento = {}".format(idLacamento)
    conn = mysql.connection.cursor()
    conn.execute(sql)
    result = conn.fetchall()
    lista = list(result)
    return lista


if __name__ == '__main__':
   mysql = MySQL(app)