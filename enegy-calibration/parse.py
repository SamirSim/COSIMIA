import json

filepath = "log-parsed-data.txt"

def get_position(node_id):
	with open("nodes.txt") as fp:
		data = fp.read()
	js = json.loads(data)
	i = 0
	while True:
		if node_id+".grenoble.iot-lab.info" == js["items"][i]["network_address"]:
			return [float(js["items"][i]["x"]), float(js["items"][i]["y"]), float(js["items"][i]["z"])]
		else:
			i = i + 1
		
def get_time(data, ip):
	stop = 0; time = 0
	with open(filepath) as fp:
		line = fp.readline()
		while stop == 0 and line:
			stop = 1

			if '00000000' in line:
				elements = line.split()
				print(elements, data)
				for i in range(1, 17):
					if elements[i] != data[i-1]:
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
			
total = 0.; cpt = 0

# Packet Delivery computing
ip_addresses = {"m3-178": "fe80::1711:6b10:65fb:5d32", "m3-179": "fe80::1711:6b10:65fd:aa36"}
"""
with open(filepath) as fp:
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
			print(time)
			if time > 0:
				total = total + time
				cpt = cpt + 1
			
			line = fp.readline()
fp.close()

print("mean latency: ", total/cpt)
"""
nodes_list = [102,103,104,105,106,108,109,110,111,112,113,114,115,120,121,122,123]
positions = []

for node in nodes_list:
	positions.append(get_position("m3-"+str(node)))

print(positions)