import xml.parsers.expat
from tkinter import *
import time
import os

cnt=0
state="idle"
current_key=""
current_value=""
fields={}
outf=None
status_label=None
last_update=time.time()
key_counts={}
phase=0
sorted_keys=[]

def update(message):
	global cnt
	global status_label
	global phase
	status_label.config(text="Phase "+str(phase)+" - "+message)
	status_label.update()

def start_element(name, attrs):
	global state
	global current_key
	global current_value
	if name=="player":
		state="player"
	elif state=="player":
		current_key=name
		
def end_element(name):
	global state
	global current_key
	global current_value
	global fields
	global cnt
	global outf
	global status_label
	global last_update
	global phase
	global key_counts
	global sorted_keys
	if state=="player":
		if name=="player":
			state="idle"
			if phase==2:
				line_list=map(lambda key:fields[key],sorted_keys)
				print("\t".join(line_list),file=outf)
			fields={}
			cnt+=1
			t=time.time()
			if (t-last_update)>=1:
				update("Processed records: "+str(cnt))
				last_update=t
		else:
			fields[current_key]=current_value
			if phase==1:
				value=current_value if not current_value=="" else "N/A"
				if current_key in key_counts:
					if value in key_counts[current_key]:
						key_counts[current_key][value]+=1
					else:
						key_counts[current_key][value]=1
				else:
					key_counts[current_key]={value:1}
			current_key=""
			current_value=""
			
def char_data(data):
	global state
	global current_key
	global current_value
	if state=="player" and not current_key=="":
		current_value=data

def process_xml_go():
	global cnt
	cnt=0
	p = xml.parsers.expat.ParserCreate()

	fh=open("players_list_xml.xml")
	
	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data

	line=True

	while((cnt<1000000) and line):

		line=fh.readline().rstrip()

		p.Parse(line)

	fh.close()
	update("Processing done, "+str(cnt)+" records processed")
	
def mkdir(path):
	if not os.path.exists(path):
		os.mkdir(path)
	
def process_xml():
	global phase
	global outf
	global sorted_keys
	phase=1
	process_xml_go();
		
	sorted_keys=list(key_counts.keys())
	sorted_keys.sort()
	
	mkdir("keycounts")
	
	for key in sorted_keys:
		print("creating keycount",key)
		keyf=open("keycounts/"+key+".txt","w")
		values=list(key_counts[key].keys())
		values.sort()
		for value in values:
			print(value+"\t"+str(key_counts[key][value]),file=keyf)
		keyf.close();
		
	phase=2
	outf=open("players.txt","w")
	print("\t".join(sorted_keys),file=outf)
	process_xml_go();
	outf.close()
	
def getkey(record,key):
		if not key in record:
			return "NA"
		return record[key] if not record[key]=="" else "NA"
	
def iterate_players_txt():
	global cnt
	global last_update
	global phase
	fh=open("players.txt")
	headers=fh.readline().rstrip().split("\t")
	line=True
	cnt=0
	collected=("country","birthday","flag")
	collections={}
	phase="Iterating players.txt"
	for key in collected:
		collections[key]={}
	while((cnt<1000000) and line):
		line=fh.readline().rstrip()
		fields=line.split("\t")
		if(line):
			cnt+=1
			record=dict(zip(headers,fields))
			for key in collected:
				subkey=getkey(record,key)
				if "rating" in record:
					touple=(int(record["rating"]),line) if not record["rating"]=="" else (0,line)
				else:
					touple=(0,line)
				if subkey in collections[key]:
					collections[key][subkey].append(touple)
				else:
					collections[key][subkey]=[touple]
			t=time.time()
			if (t-last_update)>=1:
				update("Processed records: "+str(cnt))
				last_update=t
	update("Iterating players.txt, scan ok, "+str(cnt)+" records processed")
	for key in collected:
		mkdir(key)
		for subkey in collections[key]:
			print("Generating "+key+" : "+subkey)
			outf=open(key+"/"+subkey+".txt","w")
			print("\t".join(headers),file=outf)
			l=list(map(lambda x:x[1],sorted(collections[key][subkey],key=lambda x:x[0],reverse=True)))
			print("\n".join(l),file=outf)
			outf.close()
			outf=open(key+"/"+subkey+".html","w")
			print("<table border=1><tr><td>"+"</td><td>".join(headers)+"</td></tr><tr>",file=outf)
			print("</tr><tr>".join(map(lambda x:("<td>"+"</td><td>".join(x.split("\t"))+"</td>"),l)),file=outf)
			print("</tr></table>",file=outf)
			outf.close()
	update("Iterating players.txt, done , "+str(cnt)+" records processed")
	
# mainloop
	
root=Tk()

status_label=Label(root)
status_label.pack()

process_xml_button = Button(root, text='Process XML', width=100, command=process_xml)
process_xml_button.pack()

iterate_txt_button = Button(root, text='Inerate players.txt', width=100, command=iterate_players_txt)
iterate_txt_button.pack()

root.mainloop()