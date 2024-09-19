import subprocess
import sys
import socket
import time
from random import choice
from string import ascii_lowercase
import os
import signal

def get_time(data, ip):
	stop = 0; time = 0
	with open(file_parsed) as fp:
		line = fp.readline()
		while stop == 0 and line:
			stop = 1

			if '00000000' in line:
				elements = line.split()
				print(elements, data)
				try:
					for i in range(1, 17):
						if elements[i] != data[i-1]:
							stop = 0
				except:
					stop = 0
				while 'source address' not in line:
					line = fp.readline()
				ip_address_file = line.split()[-1]
				if ip_address_file != ip:
					stop = 0
			
				if stop == 1:
					time = line_prev.split(';')[0]
					#print(data, ip, time)
					fp.close()
					return time
			else:
				line_prev = line
				line = fp.readline()
				stop = 0
		return time

nb_stations = 2 # nb. of stations
period = 1000000 # message period in µS
message_length = 10 # message length in bytes
nb_packets = 10 # max nb. of packet to be transmitted per node

init = int(sys.argv[1]) # first id of nodes
server_address = sys.argv[2] # ipv6 address of udp server
server_port = sys.argv[3] # port of udp server

ip_addresses = {}
#nodes_id_list = [102,103,104,105,106,108,109,110,111,112,113,114,115,120,121,122,123]
#nodes_id_list = [2,3,10,11,12,13,14,15,16,18,20,21,22,23,24,25,26,27,28,29]
#nodes_id_list = [71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,100,101,102,103,104,105,106,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,290,292,293,294,295,296,297]

for i in range(init, init+nb_stations):
#for i in nodes_id_list:
	if i == 107:
		continue
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print('getting m3-'+str(i)+' address')
	sock.connect(("m3-"+str(i), 20000))
	sock.send('ifconfig \n'.encode())
	time.sleep(1)
	data = sock.recv(1024).decode()
	lines = data.splitlines()
	print(lines)
	ipv6 = lines[8].split()[2].replace("/64","")
	ip_addresses["m3-"+str(i)] = ipv6
	#ip_addresses.append(elem)
	print(ip_addresses)
	sock.close()

time.sleep(2)

print('start sending')
for i in range(init, init+nb_stations):
#for i in nodes_id_list:
	if i == 107:
		continue
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(("m3-"+str(i), 20000))
	message = ''.join(choice(ascii_lowercase) for i in range(message_length)) # generate a dummy message
	sock.send('udp send '.encode()+str(server_address).encode()+' '.encode()+str(server_port).encode()+' '.encode()+str(message).encode()+' '.encode()+' '.encode()+str(nb_packets).encode()+' '.encode()+str(period).encode()+'\n'.encode())
	sock.close()
	time.sleep(0.1)

time.sleep (1)

file = "log.txt"
file_parsed = "log-parsed.txt"

os.environ['FILE'] = file
os.environ['FILEPARSED'] = file_parsed

#output = subprocess.check_output("serial_aggregator > $FILE", shell=True, text=True, stderr=subprocess.DEVNULL)
pro = subprocess.Popen("exec serial_aggregator > $FILE", stdout=subprocess.PIPE, shell=True)

execution_time = (period / 1000000) * nb_packets
time.sleep(execution_time + 2)

print('finish sending')

pro.kill()

output = subprocess.check_output("cat $FILE | grep -a -e 'Success:' -e 'PKTDUMP:' -e '00000000' -e 'source address' > $FILEPARSED", shell=True, text=True, stderr=subprocess.DEVNULL)

total = 0.; cpt = 0

# Packet latency computing
with open(file_parsed) as fp:
	line = fp.readline()
	while line:
		while "Success:" not in line and line:
			line_prev = line
			line = fp.readline()
		if line:
			data = line.split()[-1]
			sending_time = float(line.split(';')[0])
			data_ascii = [hex(int(ord(c))).lstrip("0x").upper() for c in data]
			sender_node = line.split(';')[1]
			ip = ip_addresses[sender_node]
			#print("send: ", data, sender_node, ip, sending_time)
			time = float(get_time(data_ascii, ip)) - sending_time
			#print(time)
			if time > 0:
				total = total + time
				cpt = cpt + 1
			
			line = fp.readline()
fp.close()

print("mean latency: ", total/cpt)

# Packet delivery computing
received_packets = subprocess.check_output("cat $FILE | grep -e 'total received packet' | awk 'NF>1{print $NF}' | tail -n1", shell=True, text=True, stderr=subprocess.DEVNULL)
delivery = float(received_packets)/(nb_packets*nb_stations)

print("packet delivery: ", delivery)
