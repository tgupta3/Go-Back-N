import sys
import socket
import threading
import time
import os
import random
from serverdef import *


def rdt_recv(s,p):
	global filename
	last_seq_norecv=-1
	maxseqno=-1
	initstart=1
	mss=0
	old_seq_norecv=-1
	recv_buffer=""
	s.settimeout(2)

	while True:
		try:
			data,addr=s.recvfrom(1100)
			maindata=data
		#addr=data[1]
		except:
			continue

		if not maindata:
			continue

		if initstart==1 :
			mss=len(maindata)-64
			initstart=0

		randint=random.random()

		if randint<=p:
			if old_seq_norecv!=last_seq_norecv:
				old_seq_norecv=last_seq_norecv
				print 
				print "Packet lost:-"+str((last_seq_norecv+1)*mss)
			continue



		errno, seq_no, dataText = parseDatagram(maindata, 0)
		if seq_no>maxseqno:
			maxseqno=seq_no

		if errno==0:
			if seq_no==last_seq_norecv+1:
				last_seq_norecv=seq_no
				print dataText
				recv_buffer+=dataText
				
			msg2reply=header2send2(last_seq_norecv+1,'')
			s.sendto(msg2reply,addr)

		elif errno==1:
			print "Unmatched checksum, datagram is corrupted"
			break

		elif errno==2:
			 print "Unmatched indicator, datagram is corrupted"
			 break

		else:
			if seq_no==last_seq_norecv+1:
				last_seq_norecv=seq_no
			msg2reply=header2send3(last_seq_norecv+1,'')
			s.sendto(msg2reply,addr)
			if maxseqno==last_seq_norecv:
				print "Process Completed"
				break

	print "File write completed"
	
	filesave=open(filename,'wb')
	filesave.write(recv_buffer)
	filesave.close()
	
	sys.exit(0)

os.system('fuser -k 7735/tcp')
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servername=socket.gethostbyname(socket.gethostname())
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port=int(sys.argv[1])
filename=str(sys.argv[2])
s.bind(('',port))
p=int(sys.argv[3])
rdt_recv(s,p)
