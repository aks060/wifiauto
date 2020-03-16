#!/usr/bin/python3
import os
import time
import sys
import requests as s
import sqlite3


db='db.sqlite'

skip=0
file='scan.txt'
checkpt='MAC '
m=0
fod='f'

if '-s' in sys.argv:
	skip=1

if '-m' in sys.argv:
	file='mac.txt'
	checkpt=''
	m=1

if '-d' in sys.argv:
	fod='d'

if '-ndb' in sys.argv:
	db='tmp'

con=sqlite3.connect(db)
cur=con.cursor()
if db=='tmp':
	print('executing')
	cur.execute('''CREATE TABLE IF NOT EXISTS "mactable" ("mac" TEXT, "countfail" INTEGER DEFAULT 0, "countpass" INTEGER DEFAULT 0, PRIMARY KEY("mac"))''')
	con.commit()

def up(mac, status, con):
	#global con, cur
	global file
	print('type mac: '+str(type(mac))+" type con: "+str(type(con)))
	cur=con.cursor()
	print('Updating database')
	quer="SELECT * FROM macdata WHERE mac='"+mac+"'"
	#print(quer)
	out=list(cur.execute(quer))
	#print(out)
	try:
		if len(out) ==0:
			if status==1:
				print('Inserting for pass')
				print(cur.execute("INSERT INTO macdata (mac, countpass) VALUES('"+mac+"', 1)"))
				con.commit()
			else:
				print('Inserting for fail')
				print(cur.execute("INSERT INTO macdata (mac, countfail) VALUES('"+mac+"', 1)"))
				con.commit()
		else:
			if status==1:
				print('Updating for pass')
				cur.execute("UPDATE macdata SET countpass=countpass+1 WHERE mac='"+mac+"'")
				con.commit()
			else:
				print('Updating for fail')
				cur.execute("UPDATE macdata SET countfail=countfail+1 WHERE mac='"+mac+"'")
				con.commit()
	except Exception as e:
		raise e
	cur.close()



def trymac(mac, type, f=None):
	global file
	print('trying mac: '+mac)
	os.popen('sudo ifconfig wlan0 down; sudo systemctl stop network-manager.service; sudo macchanger -m '+mac+' wlan0; sudo systemctl start network-manager.service;')
	#wok=input('Working? (y/n)')
	time.sleep(1)
	png=os.system('ping -c 1 -W 1 google.com')
	while png==512:
		png=os.system('ping -c 1 -W 1 google.com')
		time.sleep(2)
	if png==0:
		wok='y'
		up(mac, 1, con)
	else:
		wok='n'
		up(mac, 0, con)
	if wok=='y' or wok=='Y':
		pass
	elif type=='f':
		nf=open('tmpmac.txt', 'w')
		nf.write(f.read()+'\n'+mac)
		nf.close()
		f.close()
		os.popen('mv tmpmac.txt '+file)
		time.sleep(1)
	return wok


l1=os.popen('sudo pwd').read()
if l1=='':
	print('Sorry Need to be sudo user')
	exit()
else:
	print('Working')
ip=os.popen("ifconfig | grep -io '1[0-9][0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*' | grep -v '127.0.0.1'").read().strip().split('\n')[0]
#print(ip)
searchip=os.popen("ifconfig | grep -io '1[0-9][0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*\.' | grep -v '127.0.0.1' | grep -m 1 ''").read().strip().split('\n')[0]+'*'
#print(searchip)
print('search ip: '+str(searchip))
'''if skip==0:
	os.system('sudo nmap -sn '+searchip+'>scan.txt')
'''
print('continue')

if fod=='f':
	m=1
	linecnt=0
	count=int(os.popen('cat '+file+' | grep -c ""').read().strip())
	print('Working on file: '+file)
	for i in range(0,count):
		f=open(file, 'r')
		if m==0:
			mac=f.readline().split(' ')[2]
		else:
			mac=f.readline().strip()
		yn=trymac(mac, 'f', f)
		if yn=='y' or yn=='Y':
			break
elif fod=='d':
	get=cur.execute("SELECT * FROM macdata WHERE 1 ORDER BY countpass DESC, countfail")
	get=list(get)
	f=open('databasemac.txt', 'w+')
	for i in get:
		f.write(i[0]+'\n')
	f.close()
	for i in get:
		yn=trymac(i[0], 'd')
		if yn=='y' or yn=='Y':
			os.system('espeak  -s 140 "Process done successfully"')
			break
	#print(get[0][0])

'''
for i in f:
	if checkpt in i:
		if m==0:
			mac=i.split(' ')[2]
		else:
			mac=i.strip()
		print('trying mac: '+mac)
		os.popen('sudo ifconfig wlan0 down; sudo systemctl stop network-manager.service; sudo macchanger -m '+mac+' wlan0; sudo systemctl start network-manager.service;')
		wok=input('Working? (y/n)')
		if wok=='y' or wok=='Y':
			break
		#print('sleeping 2 sec')
		#getip=os.popen("ifconfig | grep -io '1[0-9][0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*' | grep -v '127.0.0.1'").read().strip().split('\n')[0]
		#print('getip: '+getip)
		#cnt=0
		#time.sleep(1)
		#while(os.popen("ifconfig | grep -io '1[0-9][0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*' | grep -v '127.0.0.1'").read().strip().split('\n')[0]==''):
		#	time.sleep(0.3)
		#newsip=os.popen("ifconfig | grep -io '1[7-9][0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*\.' | grep -m 1 ''").read().strip()+'*'
		#if newsip==searchip:
		#	ping=''
		#	try:
		#	 	ping=s.get('http://detectportal.firefox.com/success.txt', headers={'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}, allow_redirects=False, timeout=0.06).content.decode().strip()
		#	except Exception as e:
		#		print(e)				
		#	if ping=='success':
		#		if os.popen('ping -c 1 google.com').read()=='0':
		#			time.sleep(3)
		#			print('Thx, it will work')
		#			exit()
		#else:
		#	print('retrying')
		''	os.popen('sudo systemctl restart network-manager.service')
			#getip=os.popen("ifconfig | grep -io '1[0-9][0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*' | grep -v '127.0.0.1'").read().strip().split('\n')[0]
			while(os.popen("ifconfig | grep -io '1[0-9][0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*\.[0-9][0-9]*[0-9]*' | grep -v '127.0.0.1'").read().strip().split('\n')[0]==''):
				time.sleep(0.3)
			ping=''
			try:
			 	ping=s.get('http://detectportal.firefox.com/success.txt', headers={'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}, allow_redirects=False, timeout=0.06).content.decode().strip()
			except Exception as e:
			 	print(e)
			if ping=='success':
				if os.popen('ping -c 1 google.com').read()=='0':
					print('this will work thx')
					exit()
'''