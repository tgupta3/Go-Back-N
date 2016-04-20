import sys
import socket
import threading
import time
import math
from clientdef import *


def datapacket(seqtosend,data):
	global mss
	
	index=seqtosend*mss

	contenttosend=data[index:index+mss]
	if not contenttosend :
			#print "No content"
			return None
	else:
			#print contenttosend
			headersend=headertosend(seqtosend,contenttosend)
			return(headersend+contenttosend)


def rdt_send(serverip,serverport,filetotransfer):
	global seq_to_send
	global last_ack_recv
	global stopcheck
	global buf_send
	global buf_send_seq
	global expired_time
	global set_timer
	global time_thread
	global mss
	global windowsize
	global s



	filetosend=open(filetotransfer,'rb')
	completefile=filetosend.read()
	filetosend.close()
	time_thread=threading.Timer(set_timer,timerthread)
	time_thread.start()
	filesendcheck=True
	generalcheck=False
	print "Timer started"
	
	while True:
			
			
			   

			if(windowsize>len(buf_send_seq)):
				msg2send=datapacket(seq_to_send,completefile)
				
				if not msg2send:
					print "msg2send empty"
					if(filesendcheck):
						print "tg"
						filesendcheck=False
						msg2send=header2send1(seq_to_send,'END')
						msg2send+="END"

						
					elif len(buf_send_seq)==0 :
						print "breaking"
						break
					else:
						print "gen_check" 
						generalcheck=True


				if (generalcheck==False):
					#print "Sending"
				 	#print msg2send
					lock.acquire()
					s.sendto(msg2send,(serverip,serverport))
					buf_send.append(msg2send)
					buf_send_seq.append(seq_to_send)
					seq_to_send=seq_to_send+1
					lock.release()
					#print "Lock release"
				

			if(expired_time==True) and len(buf_send)>0:
					lock.acquire()
					time_thread.cancel()
					lock.release()
					lock.acquire()

					for msg2send in buf_send:
						s.sendto(msg2send,(serverip,serverport))

					lock.release()
					expired_time=False
					lock.acquire()
					time_thread=threading.Timer(set_timer,timerthread)
					time_thread.start()
					lock.release()




def ackrecv():
		global last_ack_recv
		global stopcheck
		global buf_send
		global buf_send_seq
		global expired_time
		global set_timer
		global time_thread

		recvierbuf=[]
		toDisplay = -1
  		time.sleep(0.01)
  		s.settimeout(2)
  		while stopcheck:
  			  
  			  try:
  				recv=s.recvfrom(1024)
  				recvierbuf.append(recv)

  			  except:
  			  	continue

  			  for data in recvierbuf:
  					errno,seq_no=parseDatagram(data[0],1)
  					if errno==0:
  						if len(buf_send_seq) > 0 and (seq_no >=buf_send_seq[0]):

  							diff=seq_no-buf_send_seq[0]
  							lock.acquire()
  							for che in range(diff):
  								
  								buf_send.pop(0)
  								
  								buf_send_seq.pop(0)
  								

  							lock.release()
  							recvierbuf.pop(0)
  							time_thread.cancel()
  							lock.acquire()
  							expired_time=False
  							time_thread=threading.Timer(set_timer,timerthread)
							time_thread.start()
							lock.release()
						last_ack_recv=seq_no-1
					elif(errno==1):
						print "Checksum not matched"
					elif(errno==2):
						print "Indicatio not matched"


		print "thread chal gaya"


def timerthread():
	global expired_time
	expired_time=True
	#print "Timer ludak gaya"

seq_to_send = 0
last_ack_recv = -1
stopcheck = True
buf_send= []
buf_send_seq = []
expired_time = False
set_timer = 0.1

serverip=str(sys.argv[1])
serverport=int(sys.argv[2])
filetotransfer=str(sys.argv[3])
windowsize=int(sys.argv[4])
mss=int(sys.argv[5])

print "Window Size="+str(windowsize)
print "Mss="+str(mss)

clientname=socket.gethostbyname(socket.gethostname())
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lock=threading.Lock()


ackthread=threading.Thread(target=ackrecv)
ackthread.start()
start_time=time.time()
rdt_send(serverip,serverport,filetotransfer)

while(len(buf_send)>0):
		print last_ack_recv
		print seq_to_send
		print len(buf_send)
		continue
print "Time taken:"+str(time.time()-start_time)
print "finished"
stopcheck=False
ackthread.join()
s.close()

