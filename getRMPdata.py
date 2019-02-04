# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 17:14:51 2019

@author: nhuntington-klein
"""

import urllib
import time
from re import sub
import unidecode

#Note this file is preprocessed to have
#Repec-author-URL###Lastname, Firstname
#on each line
with open('twitterhandles_firsthalf.csv','r',encoding='utf-8') as handles:
    handles = handles.read()
    
#Split each author by line
handles = handles.split('\n')
#And then split each line into Twitter handle and name. Strip blank space.
hdata = [[j.strip() for j in i.split(',', maxsplit=1)] for i in handles]
          
#and get rid of the header line
hdata = hdata[1:]


#Remove middle initials
for i in hdata:
    if i[1][-1:] == '.':
        i[1] = i[1][0:i[1].rfind(' ')]
    
    #Create a searchable name string, replacing all spaces with +
    #and getting rid of the quotes
    ns = sub(' ','+',sub('[,"]','',i[1]))
    #And get rid of accents, it messes it up
    ns = unidecode.unidecode(ns)    
    
    #Open the given profile page
    f = urllib.request.urlopen('http://www.ratemyprofessors.com/search.jsp?query='+ns)
    text = f.read()
    text = text.decode('utf-8')
    #and extract the first RMP ID we see, if there is one
    if text.find('ShowRatings.jsp?tid=') > -1 :
        text = text[text.find('ShowRatings.jsp?tid=')+20:]
        text = text[:text.find('"')]
        i.append(text)
        
        #Now go to that prof's page
        fp = urllib.request.urlopen('http://www.ratemyprofessors.com/ShowRatings.jsp?tid='+i[2])
        textp = fp.read()
        textp = textp.decode('utf-8')
        
        #The first mention of overall quality, followed by a strip, then 
        #skip over the <div class="grade" title=""> tag
        oq = textp[textp.find('Overall Quality')+15:].strip()[28:]
        #Then only take up to the end of hte div
        oq = oq[:oq.find('</div>')]
        
        #and add on
        i.append(oq)
        
        #Then look for number of reviews
        nr = textp[textp.find('<div class="table-toggle rating-count active" data-table="rating-filter">')+73:].strip()
        #And go from here to the next space
        nr = nr[:nr.find(' ')]
        
        #and add on
        i.append(nr)
        
        #Finally get department
        dep = textp[textp.find('Professor in the ')+17:].strip()
        dep = dep[:dep.find('department')-1]
        
        i.append(dep)
    #If it's not there, append two blanks
    else:
        i.append('')
        i.append('')
        i.append('')
        i.append('')
    
    
    #Keep track of where we are
    print(i[1])
    #Don't mob the thing
    time.sleep(2)
    
#Write it all out to CSV
with open('postRMPdata.csv','w',encoding='utf-8') as rmp:
    rmp.write('twitter,name,RMPID,overall.rating,num.reviews,department\n')
    
    for i in hdata:
        rmp.write(i[0]+','+i[1]+','+i[2]+','+i[3]+','+i[4]+','+i[5]+'\n')
    