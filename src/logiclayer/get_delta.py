import os
import json
from collections import Counter

deva,devb,deletedev,addedev,addlink,delink=[],[],[],[],[],[]  

def hlcomp(etc,var):
    for a in etc:
        if etc[a]!=var[a] and etc[a]!=None:
            if a!='Details':
                print("Cannot change the given parameter")
                return 0
            else:
                findev(etc['Details'],var['Details'])
                compdetails(etc['Details'],var['Details'])
		#addconns(etc['Details'], addedev)
                return 1

def addconns(etc, dev):
    #print(dev)
    al={}
    links=[]
    for item in etc:
	#print(item["Device_name"])
	if item["Device_name"] == dev:
	    for conns in item["Connections"]:
		#print("appending ", conns["Connected_to"], "for", dev)
		links.append(conns["Connected_to"])
	
    al[dev] = links
    addlink.append(al)
    #print(al)
    #print(addlink)

def delconns(var, dev):
    dl={}
    links=[]
    for item in var:
	if item["Device_name"] == dev:
	    for conns in item["Connections"]:
		links.append(conns["Connected_to"])

    dl[dev] = links
    delink.append(dl)
 
def findev(etc,var):
    for a in etc:
        if a['Device_name'] not in deva:
            deva.append(a['Device_name'])
    for b in var:
            if b['Device_name'] not in devb:
                devb.append(b['Device_name'])
    for i in deva:
        if i not in devb:
            addedev.append(i)
	    addconns(etc, i)
    for j in devb:
        if j not in deva:
            deletedev.append(j)
	    delconns(var, j)
    #print(deva)
    #print(devb)
    #print(addedev)
    #print(deletedev)
            
def comparelist(a,b):
    l=[]
    #print(a)
    #print(b)
    for i in a:
	#print(i, a[i])
        if i not in b:
	    cnt = a[i]
	    while(cnt>0):
            	l.append(i)
		cnt-=1
	elif a[i] > b[i]:
	    cnt = a[i]-b[i]
	    while(cnt>0):
		l.append(i)
		cnt-=1
    return l

def compdetails(etc,var):
    for a in etc:
        currlink,newlink=[],[]
        dl,al={},{}
        for b in var:
            if a['Device_name']==b['Device_name']:
                for i in a:   
                    if a[i]!="" and a[i]!=b[i]:
                        if i!='Connections':
                            if a['Device_name'] not in deletedev:
				#print(i)
                                deletedev.append(a['Device_name'])
                            if b['Device_name'] not in addedev:
                                addedev.append(b['Device_name'])
                        else:
                            newlink,currlink=findlinks(a[i]),findlinks(b[i])
                            #print("current",b['Device_name'],currlink,"new",a['Device_name'],newlink)
			    newlink = dict(Counter(newlink))
			    currlink = dict(Counter(currlink))
                            dl[a['Device_name']]=comparelist(currlink,newlink)
                            if dl[a['Device_name']]!=None:
                                delink.append(dl)
                            #print("dl is ",dl, "delink is", delink )
                            al[a['Device_name']]=comparelist(newlink,currlink)
                            if al[a['Device_name']]!=None:
                                addlink.append(al)
                            #print("al is", al, "addlink is", addlink)
                            ch=compconn(a[i],b[i])
                            #print("ch",ch)
                            if len(ch) != 0:
                                #print("Updating with ch")
                                if len(dl[a['Device_name']]) != 0:
                                    #print("something present dl")
                                    for li in ch:
                                        dl[a['Device_name']].append(li)
                                else:
                                    #print("nothing present dl")
                                    dl[a['Device_name']] = ch
                                if len(al[a['Device_name']]) != 0:
                                    #print("something present al")
                                    for li in ch:
                                        al[a['Device_name']].append(li)
                                else:
                                    #print("nothing present al")
                                    al[a['Device_name']] = ch
                            #print("dl is", dl, "delink is", delink, "al is", al, "addlink is", addlink)
                            #if check_if_present(a['Device_name'], delink) != 1:
                                #delink.append(dl)
                            #if check_if_present(a['Device_name'], addlink) != 1:
                                #addlink.append(al)
                            #print("delink is", delink, "addlink is", addlink)

def check_if_present(dev_name, link):
    if len(link) == 0:
        #print("returning 0 for len")
        return 0
    for item in link:
        #print(item)
        if dev_name == item[0]:
            #print("returning 1 for ", dev_name, "length", len(link))
            return 1
    #print("returning 0 for ", dev_name)
    return 0

def findlinks(files):
    currlink=[]
    for a in files:
        #if a['Connected_to'] not in currlink:
	#if a['Connected_to'] not in addedev:
            currlink.append(a['Connected_to'])
    return currlink
    
def compconn(etc,var):
    changed=False
    connto=[]
    for a in etc:
        for b in var:
            for i in a:
                    if i=='Connected_to' and a['Connected_to']==b['Connected_to'] and a[i]!="" and a[i]!=b[i]:
                            connto.append(a['Connected_to'])                          
    return connto

def rnd_update_cmp(etc,var):

    hlcomp(etc,var)

    return addedev,deletedev,addlink,delink
