from flask import Flask, flash, redirect, render_template, request, session, abort
import pandas as pd
import sys, os, markdown, praw, re
from datetime import datetime
from flask_sslify import SSLify
from textblob import TextBlob

app = Flask(__name__)
if 'DYNO' in os.environ: # only trigger SSLify if the app is running on Heroku
    sslify = SSLify(app)
reload(sys)
sys.setdefaultencoding('utf-8')
reddit = praw.Reddit(client_id='SSAdjqVlsU_TJA', client_secret='FpKThnKksTmVAsmXuXpVN4JAi_w', user_agent='theheartoftuxesarchives')
ids = ['t1_cqjez3e']

@app.route("/")
def index():
    df = pd.read_csv('heartoftuxes.csv', header=0)
    df.dropna()
    srlist = df["subreddit"].unique()
    return render_template(
        'index.html', srlist=srlist)


@app.route("/<string:subreddit>/search", methods=["POST"])
def subreddit_search(subreddit):
    df = pd.read_csv('heartoftuxes.csv', header=0)
    df_view = df.loc[df["subreddit"] == subreddit]
    df_count = len(df_view.index)
    search_string = request.form['searchstring']
    search_results = []
    for i in range(0,df_count):
      result_index=df_view.iloc[i]['body'].lower().find(search_string.lower()) 
      if result_index!=-1 :
        start_index=result_index-20
        end_index=result_index+100
        if start_index<0:
          start_index=0
        if end_index>len(df_view.iloc[i]['body']):
		  end_index=len(df_view.iloc[i]['body'])-1
        result_text="..."+df_view.iloc[i]['body'][start_index:end_index]+"..."
        result_entry = {'post_id':i ,'post_text': unicode(result_text,errors='ignore') }
        search_results.append(result_entry)
    return render_template(
        'search.html',count=df_count,subreddit=subreddit,results=search_results, search_term=search_string)

@app.route("/search_all", methods=["POST"])
def all_search():
    df = pd.read_csv('heartoftuxes.csv', header=0)
    srlist = df["subreddit"].unique()
    search_results = []
    for sr in srlist:
      df_view = df.loc[df["subreddit"] == sr]
      df_count = len(df_view.index)
      search_string = request.form['searchstring']
      for i in range(0,df_count):
        result_index=df_view.iloc[i]['body'].lower().find(search_string.lower()) 
        if result_index!=-1 :
          start_index=result_index-20
          end_index=result_index+100
          if start_index<0:
            start_index=0
          if end_index>len(df_view.iloc[i]['body']):
		    end_index=len(df_view.iloc[i]['body'])-1		
          result_text="..."+df_view.iloc[i]['body'][start_index:end_index]+"..."
          result_entry = {'post_id':i ,'post_text': unicode(result_text,errors='ignore'), 'subreddit':sr }
          search_results.append(result_entry)
    return render_template(
        'search_all.html',count=df_count,results=search_results, search_term=search_string)
		
@app.route("/<string:subreddit>")
def subreddit(subreddit):
    df = pd.read_csv('heartoftuxes.csv', header=0)
    df_view = df.loc[df["subreddit"] == subreddit]
    df_count = len(df_view.index)
    return render_template(
        'subreddit.html',count=df_count,subreddit=subreddit)
		
@app.route("/<string:subreddit>/<int:post>")
def subreddit_post(subreddit,post):
    df = pd.read_csv('heartoftuxes.csv', header=0)
    df_view = df.loc[df["subreddit"] == subreddit]
    blob = TextBlob(df_view.iloc[post]['body'])
    sentiment = blob.sentiment
	
    text = markdown.markdown(df_view.iloc[post]['body'])
    score = df_view.iloc[post]['score']
    ups = df_view.iloc[post]['ups']
    downs = df_view.iloc[post]['downs']
    df_count = len(df_view.index)
    fullname = df_view.iloc[post]['name']
    parent = "[...]"
    title = ""
    permalink ="#"
    date = "n/a"
    author =""
    
    if str(fullname).startswith('t1_'):
      comment_id = [fullname]
      for p in reddit.info(comment_id) :
        s_id = [p.parent_id]
        permalink = p.permalink
        for s in reddit.info(s_id):
          date = datetime.utcfromtimestamp(s.created_utc).strftime('%Y-%m-%d %H:%M:%S')
          author = s.author
          if str(p.parent_id).startswith('t1_'):
            parent = markdown.markdown((s.body).encode('utf8'))
            title = s.submission.title
            #print((s.body).encode('utf8'))        
            #print(s.permalink)        
          if str(p.parent_id).startswith('t3_'):
            parent = markdown.markdown(s.selftext)
            title = s.title
            print(title)
            #print(s.permalink)
            #print(s.selftext)
    return render_template(
        'main.html',sentiment=sentiment,author=author,content=text,subreddit=subreddit,permalink=permalink,post=post,title=title,parent=parent,count=df_count,score=score,date=date)


if __name__ == '__main__':
    app.run()
