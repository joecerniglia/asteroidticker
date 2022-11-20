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

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


# Stuff to initialize the Flask app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = get_random_string(20) # this can be anything
bootstrap = Bootstrap(app)

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
    global report, calday, complete_date, LD, daysago, count, lastpage, pagenum, pn

    report, calday, complete_date, LD, daysago, count, lastpage, pagenum, pn = None, None, None, None, None, None, None, None, None
    
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
            #Process the date
            d1 = str((datetime.today() - timedelta(days=daysago)).strftime('%Y-%m-%d'))
            d2 = str((datetime.today() + timedelta(days=daysago)).strftime('%Y-%m-%d'))
            datef=datetime.strptime(d1,format)
            complete_date=datef.strftime("%b %d, %Y")
            calday=calendar.day_name[datef.weekday()]
            f = (r"https://ssd-api.jpl.nasa.gov/cad.api?dist-max=" + LD_str + "LD&date-min=" + d1 + "&date-max=" + d2 + "&sort=dist")
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
                report=report+['This near-Earth object' + timeref + 'ranked #' + str(n+1) + ' in proximity to Earth.']
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
                lastpage=int(count/2+(1-(count%2/2)))
            else:
                lastpage=int(count/3+(1-(count%3/3)))
            if count==0:
                #session['report'] = 'None'
                report = 'None'
            #else:
                #session['report'] = report
            #session['calday'] = calday
            #session['complete_date'] = complete_date
            #session['LD'] = LD
            #session['daysago'] = daysago
            #session['count'] = count
            #session['lastpage'] = lastpage

            if 1<LD:
                pn=21
            else:
                pn=16

            if daysago==None:
                return 'The NASA server is busy right now. Try again later, or try reducing the size of your parameters.'
            else:
                try:
                    #return report
                    return redirect(url_for('reportout', pagenum=1))
                except Exception as e:
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
    
    time.sleep(5)

    return render_template('form2.html', report=PageResult(report, int(pagenum.replace('.0','')), pn),
    calday=calday,complete_date=complete_date,LD=LD,
    daysago=daysago,count=count,lastpage=int(lastpage.replace('.0',''))



if __name__ == '__main__':
    app.run()

