# -*- coding:utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
# from spider import get_html

import PySearchEngineNN
#import importlib
#importlib.reload(PySearchEngineNN)
searcher = PySearchEngineNN.Searcher('G:/searchindex.db')


app = Flask(__name__)
@app.route('/', methods=['post', 'get'])
def search():
    query = request.form.get('query')
    print(query)
    if query is None:
        query = " "
        return render_template('search.html')
    results=searcher.getQuery(query)
    #quotes = Quotes.query.filter(Quotes.content.like("%"+content+"%")if content is not None else "").all()
    #return render_template('search.html',quotes = quotes) 
    return render_template('search.html',quotes = results)
 
def search1():
	return render_template('search.html')

if __name__ == "__main__":
	app.run(debug=True)