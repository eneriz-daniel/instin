import os
import pyvisa
import socket
from time import sleep

port = 50002 #If configuring more than one gateway, ensure to setup them with different ports

N_links = 5
BUFF = 1024*8

def fillp2(path: str) -> int:
    """Auxiliary function for file transfer.

    Expands the file of the input path to have a size multiple of 512

    Args:
        path: Input file path

    Returns:
        The new input file lenght

    """
    file = open(path, 'rb')
    file_len = len(file.read())
    file.close()

    new_file_len = 512

    while new_file_len < file_len:
        new_file_len = new_file_len + 512

    file = open(path, 'ab')
    for k in range(new_file_len - file_len):
        file.write(b'\n')
    file.close()
    
    return new_file_len

def send_msg(host: socket.socket, msg: str) -> None:
    data = msg.encode('ASCII')
    host.send(data)

def receive_msg(host):
    data = host.recv(BUFF)
    msg = data.decode('ASCII')

    return msg

def launch_program(host, path_in):
    #Receiving program to run
    fin = open(path_in,'wb')
    
    n_paths_out = receive_msg(host)
    print('Output files number: '+n_paths_out)
    send_msg(host, 'Output files number'+ n_paths_out)
    
    paths_out = []
    
    for pout in range(int(n_paths_out)):
        paths_out.append(receive_msg(host))
        send_msg(host, 'Output file '+str(pout)+':'+paths_out[pout])
    
    #Receiving the input file length
    fin_lengh = receive_msg(host)
    print(int(fin_lengh))
    print('Input file length ' + fin_lengh)
    
    send_msg(host, 'Input file length '+fin_lengh)

    print('Receiving input file')
    n_paq = int(fin_lengh)/512
    print(n_paq)
    for k in range(int(n_paq)):
        data = host.recv(512)
        print(data)
        fin.write(data)
    fin.close()

    send_msg(host, 'Input file received')
    
    print('Running input file')
    os.system('sudo python3 '+path_in)
    print('Input file execution completed, sending output files to host')
    
    for pout in range(int(n_paths_out)): #Sending output files
        print(receive_msg(host))
        
        leng = fillp2(paths_out[pout])
        print('Output file ' + str(pout) + ' length: '+ str(leng))
        
        n_paq = int(leng)/512.0 #Sending the number of packets to receive
        send_msg(host, str(n_paq))
        print(n_paq)
        
        file_out = open(paths_out[pout],'rb')
        
        print(receive_msg(host))

        for k in range(int(n_paq)): #Sending the packets of the output file
            data = file_out.read(512)
            print(data)
            host.send(data)
            sleep(0.2)
        
        file_out.close()
        
        sleep(1)
        

    print('Output files sent')


rm=pyvisa.ResourceManager('@py') #Using pyvisa-py drivers

#Creating the socket object:
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Reusing the same port
try:
    s.bind(('', port))
except socket.error as err:
    print('Bind failed')
    print(err)
s.listen(N_links) #Limiting the number of clients able to connect to the gateway
print('Socket awaiting messages')

(conn, addr) = s.accept() #Connecting to the host
print('Connected to ' + str(addr))
msg = receive_msg(conn)
os.system('sudo date ' + msg) #Setting the datetime
conn.close()

print('Program start')

inst = []
inst.append(0)

while True:
    (conn, addr) = s.accept()
    print('Connected to ' + str(addr))
    
    msg = receive_msg(conn) #Receiving a packet from host
    print("Packet received: "+msg)
    
    if msg[0] == 'p':
        send_msg(conn, 'Launching '+msg[1:])
        launch_program(conn, msg[1:])
    else:
        n_inst = int(msg[0])
        msg = msg[1:]

        if n_inst == 0: #If header is a '0' it is an opening-instrument order
            print("Opening instrument...")

            try:
                inst.append(rm.open_resource(msg))
                send_msg(conn, str(len(inst)-1)) #Sending back the position in the instrument tuple, that is de ID
                print("Ok!\n")

            #Possible errors handling
            except IndexError:
                send_msg(conn, "IndexError: VISA not correct")
                print('Error\n')
            except ValueError:
                send_msg(conn, "ValueError: VISA not correct")
                print('Error\n')
            except pyvisa.errors.VisaIOError:
                send_msg(conn, "VisaIOError: Insufficient location information or the requested device or resource is not present in the system.")
                print('Error\n')
            except:
                send_msg(conn, "Unexpected Error")
                print('Error\n')
        
        #If the header is not '0', then it is the instrument where the order must be done ID
        elif '?' in msg: #If the data in the packet has a '?' it is a query statement
            print("Query received...")
            try:
                data = inst[n_inst].query(msg)
                send_msg(conn, str(data)) #Sending the queried data
                print("Ok!\n")
            
            #Possible errors handling
            except pyvisa.errors.VisaIOError:
                send_msg(conn, 'VisaIOError: Visa communication error on query')
                print("Error\n")
            except:
                send_msg(conn, 'Unexpected Error')
                print("Error\n")

        elif msg == 'close': #If data in the packet is 'close' then is a reboot order
            conn.close()
            s.close()
            os.system('reboot')

        else: #If it is not none of those, it must be a query statement
            inst[n_inst].write(msg)

    conn.close()