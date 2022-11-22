import os
import click
from flask.cli import with_appcontext
import requests
import json
import webbrowser
from datetime import datetime, timedelta
from datetime import date
import time
import calendar
import numpy as np
import math
from flask import Flask, request, render_template, redirect, url_for #, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import TextAreaField
import random
import string
from flask_sqlalchemy import SQLAlchemy
#import settings
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
#SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = False




db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
app.cli.add_command(create_tables)

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()

def create_app(config_file='settings.py'):
    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config.from_pyfile(config_file)

    app.config['SECRET_KEY'] = 'hard to guess string'
    app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bootstrap = Bootstrap(app)

    app.cli.add_command(create_tables)

    return app

#app = create_app()


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class State(db.Model):
    __tablename__='states'
    id=db.Column(db.Integer, primary_key=True)
    report=db.Column(db.Text)
    calday = db.Column(db.String(64))
    complete_date = db.Column(db.String(64))
    LD = db.Column(db.Integer)
    daysago = db.Column(db.Integer)
    count = db.Column(db.Integer)
    lastpage=db.Column(db.Integer)
    pn=db.Column(db.Integer)

def createList(r1, r2):
 # Testing if range r1 and r2
 # are equal
 if (r1 == r2):
     return r1
 else:
  # Create empty list
  res = []
  # loop to append successors to
  # list until r2 is reached.
  while(r1 > r2-1 ):
      res.append(r1)
      r1 -= 1
  return res

# Driver Code

class ReportForm(FlaskForm):
    report = TextAreaField()

# This decorator tells Flask to use this function as a webpage handler/renderer
@app.route('/', methods=['GET', 'POST'])
def daysnlunar():
    #global report, calday, complete_date, LD, daysago, count, lastpage, pn, pagenum
    global report, pn, pagenum, lastpage
    #for all records
    db.session.query(State).delete()
    db.session.commit()
    #LD=0
    #LD_str=''
    #daysago=9
    #d1=''

    day_selection=[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0,'']
    r1, r2 = 15, 0
    LD_selection=createList(r1, r2)
    format = '%Y-%m-%d'
    if request.method == 'POST':
        #GET DAYS AGO AND LUNAR DISTANCE PARAMETERS
        # Check which button was pressed
        submit = request.form.get('submit')
        clear = request.form.get('clear')
        if submit == 'Submit':
            daysago = int(request.form.get('daysago'))
            LD_str = str(request.form.get('LD'))
            LD = int(request.form.get('LD'))
            sort=request.form.get("sort")
            if sort=='size':
                s1='h'
                s1_desc='size'
            else:
                s1='dist'
                s1_desc='proximity to Earth'
            #Process the date
            d1 = str((datetime.today() - timedelta(days=daysago)).strftime('%Y-%m-%d'))
            d2 = str((datetime.today() + timedelta(days=daysago)).strftime('%Y-%m-%d'))
            datef=datetime.strptime(d1,format)
            complete_date=datef.strftime("%b %d, %Y")
            calday=calendar.day_name[datef.weekday()]
            f = (r"https://ssd-api.jpl.nasa.gov/cad.api?dist-max=" + LD_str + "LD&date-min=" + d1 + "&date-max=" + d2 + "&sort=" + s1)
            data = requests.get(f)
            t = json.loads(data.text)
            source=t['signature']['source']
            count = int(t['count'])
            #MAKE A REPORT ABOUT ASTEROIDS
            report=[]
            for n in range(count):
                object = t['data'][n]
                try:
                    dlow = str("{0:,.0f}".format((1329/math.sqrt(.25))*(10**(-0.2*float(object[10])))*3280.84))
                except:
                    dlow=''
                try:
                    dhigh = str("{0:,.0f}".format((1329/math.sqrt(.05))*(10**(-0.2*float(object[10])))*3280.84))
                except:
                    dhigh=''
                report=report + ['The object named (' + object[0] +') ']
                miles=str("{0:,.0f}".format(np.round(float(object[4])*92955807.267433,decimals=2)))
                format2 = '%Y-%b-%d'
                if datetime.strptime(object[3][:11],format2) < datetime.today(
                ) and datetime.strptime(object[3][:11],format2) + timedelta(
                days=1) > datetime.today():
                        timeref=' is now '
                elif datetime.strptime(object[3][:11],format2) < datetime.today():
                    timeref=' was '
                elif datetime.strptime(object[3][:11],format2) > datetime.today():
                    timeref=' will be '
                report=report+[timeref[1:] + miles + ' miles from Earth on ' + object[3][:11] + ' (the moon is 238,854 miles away)']
                if int(miles.replace(",", ""))<238854:
                    report=report+['--This object' + timeref + 'closer to the Earth than the Moon!--']
                report=report+['and is between ' + dlow + ' and ' + dhigh + ' feet across.']
                report=report+['This near-Earth object' + timeref + 'ranked #' + str(n+1) + ' in ' + s1_desc + '.']
                #report=report+["https://watchers.news/?s=" + object[0] + "&post_type=post"]
                from urllib import request as ur
                if LD<=10 and daysago<=10:
                    try:
                        if int(miles.replace(',',''))>4000:
                            ur.urlopen("https://theskylive.com/will-asteroid-" + object[0].replace(' ','').lower() + "-impact-earth")
                            report=report+["https://theskylive.com/will-asteroid-" + object[0].replace(' ','').lower() + "-impact-earth"]
                        else:
                            report=report+["https://www.google.com/search?q=" + object[0] + "+asteroid"]
                    except ur.HTTPError as e:
                        #print(e.code)
                        report=report+["no skylive weblink available"]
                    except ur.URLError as e:
                        #print(e.args)
                        report=report+["no skylive weblink available"]
                else:
                    report=report+["For skylive weblink, choose parameters <= 10."]
                if LD<=10 and daysago<=10:
                    try:
                        ur.urlopen("https://www.spacereference.org/asteroid/" + object[0].replace(' ','-').lower())
                        report=report+["https://www.spacereference.org/asteroid/" + object[0].replace(' ','-').lower()]
                    except ur.HTTPError as e:
                        report=report+["no spacereference weblink available"]
                    except ur.URLError as e:
                        report=report+["no spacereference weblink available"]
                else:
                    report=report+["For spacereference weblink, choose parameters <= 10."]

                report=report+['break']
            if LD==1:
                #ceiling: will need compensation in the form. For example for 27 objects on 3-per-page, this gives 10
                if count%2==0:
                    lastpage=int(str(count/2).replace('.0',''))
                else:
                    lastpage=int(str(count/2+(1-(count%2/2))).replace('.0',''))
            else:
                if count%3==0:
                    lastpage=int(str(count/3).replace('.0',''))
                else:
                    lastpage=int(str(count/3+(1-(count%3/3))).replace('.0',''))
            if count==0:
                #session['report'] = 'None'
                report = 'None'

            if 1<LD:
                pn=21
            else:
                pn=16

            state=State(report=str(report), calday=calday, complete_date=complete_date,
            LD=LD, daysago=daysago, count=count, lastpage=lastpage, pn=pn)
            db.session.add(state)
            db.session.commit()


            if daysago==None:
                return 'The NASA server is busy right now. Try again later, or try reducing the size of your parameters.'
            else:
                try:
                    #return pagenum
                    #return str(len(report))
                    return redirect(url_for('reportout', pagenum=1))
                except Exception as e:
                    #return pagenum
                    return str(e)
                    #return 'The NASA server is busy right now. Try again later, or try reducing the size of your parameters.'

        elif clear=='Clear':
            return render_template('form.html',day_selection=day_selection,LD_selection=LD_selection)#params to populate drop-downs
    try:
        return render_template('form.html',day_selection=day_selection,LD_selection=LD_selection)#params to populate drop-downs
    except:
        return "Please enter both your asteroidal parameters."


class PageResult:
   def __init__(self, data, page = 1, number = 21):
     self.__dict__ = dict(zip(['data', 'page', 'number'], [data, page, number]))
     self.full_listing = [self.data[i:i+number] for i in range(0, len(self.data), number)]
   def __iter__(self):
     for i in self.full_listing[self.page-1]:
       yield i
   def __repr__(self): #used for page linking
     return "/reportout/{}".format(self.page+1) #view the next page

@app.route('/reportout/<pagenum>', methods=['GET'])
def reportout(pagenum):

    #time.sleep(6+count*.5)
    table_name='states'

    column_name='report'
    query= f'SELECT {column_name} FROM {table_name}'
    reportd=db.session.execute(query)
    report=reportd.fetchall()
    report = eval(report[0][0])

    column_name='pn'
    query= f'SELECT {column_name} FROM {table_name}'
    pnd=db.session.execute(query)
    pn=pnd.fetchall()
    pn = int(str(pn[0][0]))

    column_name='lastpage'
    query= f'SELECT {column_name} FROM {table_name}'
    lastpaged=db.session.execute(query)
    lastpage=lastpaged.fetchall()
    lastpage = int(str(lastpage[0][0]))

    column_name='calday'
    query= f'SELECT {column_name} FROM {table_name}'
    caldayd=db.session.execute(query)
    calday=caldayd.fetchall()
    calday = str(calday[0][0])

    column_name='complete_date'
    query= f'SELECT {column_name} FROM {table_name}'
    complete_dated=db.session.execute(query)
    complete_date=complete_dated.fetchall()
    complete_date = str(complete_date[0][0])

    column_name='LD'
    query= f'SELECT {column_name} FROM {table_name}'
    LDd=db.session.execute(query)
    LD=LDd.fetchall()
    LD=int(str(LD[0][0]))

    column_name='daysago'
    query= f'SELECT {column_name} FROM {table_name}'
    daysagod=db.session.execute(query)
    daysago=daysagod.fetchall()
    daysago=int(str(daysago[0][0]))

    column_name='count'
    query= f'SELECT {column_name} FROM {table_name}'
    countd=db.session.execute(query)
    count=countd.fetchall()
    count=int(str(count[0][0]))

    #return str(lastpage)
    return render_template('form2.html', report=PageResult(report, int(pagenum), pn),
    calday=calday,complete_date=complete_date,LD=LD,
    daysago=daysago,count=count,lastpage=int(str(lastpage).replace('.0','')))

@app.errorhandler(500)
def server_overloaded(error):
    return render_template('500.html'), 500




if __name__ == '__main__':
    app.run()
