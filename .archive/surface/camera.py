import socket,cv2, pickle,struct

# cap = cv2.VideoCapture(0)

# create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '192.168.0.101' # paste your server ip address here
port = 10000
client_socket.connect((host_ip,port)) # a tuple
data = b""
payload_size = struct.calcsize("Q")
# print("size",payload_size)
while True:
# 	print("data size",len(data))
	while len(data) < payload_size:
		packet = client_socket.recv(4*1024) # 4K	hoi;,,
		print("packet recieved")
# 		print("packet size",len(packet))
		if not packet: break
		data+=packet
	packed_msg_size = data[:payload_size]
	data = data[payload_size:]
	msg_size = struct.unpack("Q",packed_msg_size)[0]
	
	while len(data) < msg_size:
		data += client_socket.recv(4*1024)
	frame_data = data[:msg_size]
	data  = data[msg_size:]
	frame = pickle.loads(frame_data)
# 	ret, frame = cap.read()
	cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
	cv2.imshow("RECEIVING VIDEO",frame)
#	cv2.waitKey(20)
	if cv2.waitKey(1) == '13':
		break 
client_socket.close()
# cap.release()
cv2.destroyAllWindows()