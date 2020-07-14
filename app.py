# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 02:25:26 2020

@author: Muhammed Ali Kocabey
@web: https://www.muhammedalikocabey.com/
"""


from evds import evdsAPI
from flask import Flask, Markup, render_template, redirect, url_for
import numpy as np


evds = evdsAPI('EVDS_API_KEY', lang="ENG") # To Get the EVDS_API_KEY --> https://evds2.tcmb.gov.tr/help/videos/EVDS_PYTHON_Kullanim_Kilavuzu.pdf

data_list = list()

start_year = 2015

for i in range(5):
    data = evds.get_data(["TP.KKHARTUT.KT1"],
                     startdate="01-01-"+str(start_year),
                     enddate="01-01-"+str(start_year+1),
                     raw=True,
                     )
    
    data_list.append([[j["YEARWEEK"], j["Tarih"], j["TP_KKHARTUT_KT1"]] for j in data])
    start_year = start_year+1


#%% manipulate data

all_data = list()
for i in range(len(data_list)):
    data_list[i][0].append(0)
    data_list[i][0].append("% 0")
    start_of_year = data_list[i][0][2]
    
    for j in range(len(data_list[i])):
        if j != 0:
            percent = round((((int(data_list[i][j][2]) - int(start_of_year))/int(start_of_year)) * 100), 2)
            data_list[i][j].append(percent)
            data_list[i][j].append(("% "+str(percent)))
            
        all_data.append(data_list[i][j])
        
        
#%% Flask Web            

app = Flask(__name__)

labels = list()

split_list = np.array_split(all_data, int((len(all_data)/20)))
split_list = [i.tolist() for i in split_list]




colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

@app.route("/")
def home():
    return redirect(url_for("line", page_number=1))

@app.route('/bar/<int:page_number>')
def bar(page_number):
    page_count = len(split_list)
    if (page_number > page_count):
        return redirect(url_for("bar", page_number=1))
    
    if (page_number < 1):
        return redirect(url_for("bar", page_number=page_count))
    bar_values = [i[3] for i in split_list[page_number-1]]
    bar_labels = [i[1] for i in split_list[page_number-1]]
    
    
    return render_template('bar_chart.html', title='In the last 5 years: Percentage of weekly Credit Card expenditure by year', max=100, labels=bar_labels, values=bar_values, page_number=page_number, page_count=page_count)



@app.route('/line/<int:page_number>')
def line(page_number):
    page_count = len(split_list)
    if (page_number > page_count):
        return redirect(url_for("line",page_number=1))
    if (page_number < 1):
        return redirect(url_for("line", page_number=page_count))
    line_values = [i[3] for i in split_list[page_number-1]]
    line_labels = [i[1] for i in split_list[page_number-1]]
    return render_template('line_chart.html', title='In the last 5 years: Percentage of weekly Credit Card expenditure by year', max=100, labels=line_labels, values=line_values, page_number=page_number, page_count=page_count)
    

@app.errorhandler(500)
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for("line", page_number=1))


if __name__ == "__main__":
    app.run()
