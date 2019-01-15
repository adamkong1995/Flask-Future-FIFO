from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():

    conn = sqlite3.connect('future.db')
    c = conn.cursor()
    #c.execute("DROP TABLE future")
    if request.method == "GET":
        c.execute("CREATE TABLE IF NOT EXISTS future(ID INTEGER NOT NULL PRIMARY KEY, ticker VARCHAR(10) NOT NULL, txDate INT NOT NULL, amount INT NOT NULL);")

        df = pd.read_sql_query("SELECT * FROM future;", conn)
        df = df.sort_values(by=['ticker', 'txDate'])
        dfAfter = df
        if df.shape[0] > 0:
            
            dfAfter['PN'] = np.where(dfAfter['amount'] > 0, 'P', 'N')
            dfAfter['CS'] = dfAfter.groupby(['ticker', 'PN'])['amount'].cumsum()
            print(dfAfter)
            dfAfter = dfAfter.groupby(['ticker'], as_index=False)\
                .apply(FiFo) \
                .drop(['CS', 'PN'], axis=1) \
                .reset_index(drop=True)

            dfAfter = dfAfter[dfAfter['amount'] > 0]

        conn.close()
        return render_template("index.html", df=df, dfAfter=dfAfter)
    else:
        print(request.form['submitButton'])
        if request.form['submitButton'] == "reset":
            c.execute("DROP TABLE future")
            conn.close()
            return redirect("/")
        else:
            date = request.form.get('date')
            ticker = request.form.get('ticker')
            amount = request.form.get('amount')

            c.execute('INSERT INTO future(ticker, txDate, amount) VALUES (?,?,?)', ( ticker, date, amount))

            conn.commit()
            conn.close()
            return redirect("/")


def FiFo(dfg):
    if dfg[dfg['CS'] < 0]['amount'].count():
        subT = dfg[dfg['CS'] < 0]['CS'].iloc[-1]
        dfg['amount'] = np.where((dfg['CS'] + subT) <= 0, 0, dfg['amount'])
        dfg = dfg[dfg['amount'] > 0]
        if (len(dfg) > 0):
            dfg['amount'].iloc[0] = dfg['CS'].iloc[0] + subT
    return dfg


if __name__ == ("__main__"):
    app.run(debug = True)