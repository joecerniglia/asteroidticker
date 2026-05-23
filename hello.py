import wikipedia
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
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import TextAreaField
import random
import string
from flask_sqlalchemy import SQLAlchemy
from urllib import request as ur
from flask import session

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

@app.before_request
def func():
  session.modified = True

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('HEROKU_POSTGRESQL_CRIMSON_URL').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

class State(db.Model):
    __tablename__='states'
    id=db.Column(db.Integer, primary_key=True)
    report=db.Column(db.Text)
    calday = db.Column(db.String(64))
    complete_date = db.Column(db.String(64))
    ld = db.Column(db.Integer)
    daysago = db.Column(db.Integer)
    count = db.Column(db.Integer)
    lastpage=db.Column(db.Integer)
    pn=db.Column(db.Integer)
    
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, State=State)

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

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
    
    global pagenum
    #for all records
    db.session.query(State).delete()
    db.session.commit()
    #day_selection=[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0,'']
    #r1, r2 = 9000, 0
    r1, r2 = 3650, 1
    day_selection=createList(r1, r2)
    r1, r2 = 50, 1
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
            if daysago>50 and LD>1:
                flash("You selected " + str(daysago) + " days for your time window. To keep results manageable, time windows greater than 50 will be processed with 1 lunar distance.")
                LD_str="1"
                LD=1
            sort=request.form.get("sort")
            if sort=='size':
                s1='h'
                s1_desc='size'
            else:
                s1='dist'
                s1_desc='proximity to Earth'
            #Process the date
            d1 = str((datetime.utcnow() - timedelta(days=daysago)).strftime('%Y-%m-%d'))
            d2 = str((datetime.utcnow() + timedelta(days=daysago)).strftime('%Y-%m-%d'))
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
                object_name=object[0]
      
                if '99942' in object_name:
                    object_name='99942 Apophis'
                elif object_name=='153814':
                    object_name='(153814) 2001 WN5'
                elif object_name=='367943':
                    object_name='367943 Duende'
                elif object_name=='2019 OD':
                    object_name='2019 OK'
                try:
                    dlow = str("{0:,.0f}".format((1329/math.sqrt(.25))*(10**(-0.2*float(object[10])))*3280.84))
                except:
                    dlow=''
                try:
                    dhigh = str("{0:,.0f}".format((1329/math.sqrt(.05))*(10**(-0.2*float(object[10])))*3280.84))
                except:
                    dhigh=''
                # FIX: Set a custom, descriptive User-Agent required by Wikipedia's policy
                # Replace the email with your own contact email
                wikipedia.set_user_agent("MyFlaskCrawlerApp/1.0 (contact: youremail@example.com)")
                
                # Your original logic block
                if (0 <= n <= 24) and daysago > 10:
                    try:
                        # Fetch the page safely without auto-suggest or redirects modifying your target
                        page = wikipedia.page(object_name.replace(" ", "_"), auto_suggest=False, redirect=False)
                        wiki = page.url
                        
                    except wikipedia.exceptions.PageError:
                        print(f"Error: Page not found for {object_name}")  # Debug aid
                        wiki = ""
                        
                    except wikipedia.exceptions.DisambiguationError as e:
                        print(f"Error: Disambiguation page. Options: {e.options}")  # Debug aid
                        wiki = ""
                        
                    except Exception as e:
                        # Prints the real error to your Flask console if something else breaks
                        print(f"Unexpected error crawling Wikipedia: {e}")
                        wiki = ""
                else:
                    wiki = ""                #HTML will not print out empty strings
                report=report + ['The object named (' + object_name +') ']
                #if wiki:
                report=report+[wiki]
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
                else:
                    report=report+['--This object' + timeref + 'beyond the orbit of the Moon.--']
                report=report+['and is between ' + dlow + ' and ' + dhigh + ' feet across.']
                report=report+['Within search parameters, this near-Earth object' + timeref + 'ranked #' + str(n+1) + ' in ' + s1_desc + '.']
                #report=report+["https://watchers.news/?s=" + object[0] + "&post_type=post"]
                
                if LD<=50 and daysago<=10:
                    try:
                        if int(miles.replace(',',''))>4000:
                            #ur.urlopen("https://theskylive.com/will-asteroid-" + object[0].replace(' ','').lower() + "-impact-earth")
                            ur.urlopen("https://theskylive.com/" + object[0].replace(' ','').lower() + "-info")
                            #report=report+["https://theskylive.com/will-asteroid-" + object[0].replace(' ','').lower() + "-impact-earth"]
                            report = report+["https://theskylive.com/" + object[0].replace(' ','').lower() + "-info"]
                        else:
                            report=report+["https://www.google.com/search?q=" + object[0] + "+asteroid"]
                    except ur.HTTPError as e:
                        #print(e.code)
                        report=report+["no skylive weblink available"]
                    except ur.URLError as e:
                        #print(e.args)
                        report=report+["no skylive weblink available"]
                else:
                    report=report+["For skylive weblink, select a time window <=10."]
                if LD<=50 and daysago<=10:
                    try:
                        ur.urlopen("https://www.spacereference.org/asteroid/" + object[0].replace(' ','-').lower())
                        report=report+["https://www.spacereference.org/asteroid/" + object[0].replace(' ','-').lower()]
                    except ur.HTTPError as e:
                        report=report+["no spacereference weblink available"]
                    except ur.URLError as e:
                        report=report+["no spacereference weblink available"]
                else:
                    report=report+["For spacereference weblink, select a time window <=10."]

                report=report+['break']
            #if LD==1:
                #ceiling: will need compensation in the form. For example for 27 objects on 3-per-page, this gives 10
            
            if count%2==0:
                 lastpage=int(str(count/2).replace('.0',''))
            else:
                 lastpage=int(str(count/2+(1-(count%2/2))).replace('.0',''))
            #else:
                #if count%3==0:
                    #lastpage=int(str(count/3).replace('.0',''))
                #else:
                    #lastpage=int(str(count/3+(1-(count%3/3))).replace('.0',''))
            if count==0:
                report = ['None']

            if daysago>365:
                pn=18
            else:
                pn=18

            state=State(report=str(report), calday=calday, complete_date=complete_date,
            ld=LD, daysago=daysago, count=count, lastpage=lastpage, pn=pn)
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
    pagenum = int(pagenum)
    
    # 1. Fetch your stored search criteria from the DB
    state_data = db.session.query(State).first()
    if not state_data:
        return redirect(url_for('daysnlunar'))
        
    # Re-fetch the data array from NASA securely using saved parameters
    d1 = str((datetime.utcnow() - timedelta(days=state_data.daysago)).strftime('%Y-%m-%d'))
    d2 = str((datetime.utcnow() + timedelta(days=state_data.daysago)).strftime('%Y-%m-%d'))
    sort_type = 'h' if state_data.pn == 18 else 'dist'
    
    f = (r"https://nasa.gov" + str(state_data.ld) + "LD&date-min=" + d1 + "&date-max=" + d2 + "&sort=" + sort_type)
    data = requests.get(f)
    t = json.loads(data.text)
    
    raw_asteroids = t.get('data', [])
    s1_desc = 'size' if sort_type == 'h' else 'proximity to Earth'
    
    # 2. Process and filter the complete dataset BEFORE slicing pages
    all_clean_lines = []
    visible_count = 0
    
    for idx, object in enumerate(raw_asteroids):
        object_name = object[0]
        
        # === BULLETPROOF ASTEROID FILTER STEP ===
        if object_name.strip() == "2026 JN4":
            continue # Drops the entire item instantly before any lines are built!
        # ========================================
            
        visible_count += 1
        
        if '99942' in object_name: object_name='99942 Apophis'
        elif object_name=='153814': object_name='(153814) 2001 WN5'
        elif object_name=='367943': object_name='367943 Duende'
        elif object_name=='2019 OD': object_name='2019 OK'
        
        try:
            dlow = str("{0:,.0f}".format((1329/math.sqrt(.25))*(10**(-0.2*float(object[10])))*3280.84))
            dhigh = str("{0:,.0f}".format((1329/math.sqrt(.05))*(10**(-0.2*float(object[10])))*3280.84))
        except:
            dlow, dhigh = '', ''
            
        miles = str("{0:,.0f}".format(np.round(float(object[4])*92955807.267433,decimals=2)))
        
        # Compile all lines for this valid asteroid
        all_clean_lines.append('The object named (' + object_name +') ')
        all_clean_lines.append(' was ' + miles + ' miles from Earth on ' + object[3][:11])
        all_clean_lines.append('and is between ' + dlow + ' and ' + dhigh + ' feet across.')
        all_clean_lines.append('Within search parameters, this near-Earth object ranked #' + str(idx + 1) + ' in ' + s1_desc + '.')
        
        if state_data.ld <= 50 and state_data.daysago <= 10:
            all_clean_lines.append("https://theskylive.com/" + object[0].replace(' ','').lower() + "-info")
        else:
            all_clean_lines.append("For skylive weblink, select a time window <=10.")
            
        all_clean_lines.append('break')

    # 3. Dynamic layout line slicing for the requested page
    # Since each asteroid has exactly 6 lines (including 'break'), 2 asteroids = 12 lines
    start_line_idx = (pagenum - 1) * 12
    end_line_idx = start_line_idx * 12 + 12
    page_report_lines = all_clean_lines[start_line_idx:end_line_idx]
    
    # 4. Calculate real page counts based on the updated visible dataset
    calculated_lastpage = math.ceil(visible_count / 2) if visible_count > 0 else 1

    class CleanPagination:
        def __init__(self, page): self.page = page
    
    return render_template(
        'form2.html', 
        report=page_report_lines, 
        pagination_state=CleanPagination(pagenum),
        calday=state_data.calday,
        complete_date=state_data.complete_date,
        LD=state_data.ld, 
        daysago=state_data.daysago,
        count=visible_count, # Displays the true filtered count on screen
        lastpage=calculated_lastpage # Directs the Last button flawlessly
    )


@app.errorhandler(500)
def server_overloaded(error):
    return render_template('500.html'), 500

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()
app.cli.add_command(create_tables)


if __name__ == '__main__':
    app.run()
