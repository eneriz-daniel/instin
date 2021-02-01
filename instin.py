import socket
import sys
import time

t_ret = 0.05 #Time between TCP connection and TCP connection
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

def sincro(IP: str, PORT: int) -> None:
    """Sends the time to the Gateway.
    
    Sends :code:`time.strftime('%m%d%H%M.%S')` to the Gateway in the IP through the PORT.

    Args:
        IP: Gateway's IP
        PORT: TCP port 
    """
    #Creating connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print('Socket creation error:')
        print(err)
        sys.exit()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.connect((IP, PORT))
    #print('Socket created')

    #Sending time
    data = time.strftime('%m%d%H%M.%S').encode('ASCII')
    s.send(data) 

    s.close() #Close connection

    time.sleep(t_ret)

def open_inst(IP: str, PORT: int, VISA:str) -> int:
    """For opening instruments in the Gateway.

    The instrument whose VISA address is VISA is opened
    in the Gateway The IP and the PORT are needed as always.
    An example of VISA address: :code:`USB0::0x0957::0x179B::MY51250760::INSTR`

    Args:
        IP: Gateway's IP
        PORT: TCP port
        VISA: Instrument's VISA address

    Returns:
        The integer identifier the Gateways has associated to the instrument.
    """
    #Creating connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print('Socket creation error:')
        print(err)
        sys.exit()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((IP, PORT))
    #print('Socket created')

    #In this case the header is 0, as it is the associated to this feature
    #The data is the VISA address
    msg = '0' + VISA 
    data = msg.encode('ASCII')
    s.send(data)

    time.sleep(t_ret)
    del(msg)

    #The ID associated to the instrument in the GW is sent back
    data = s.recv(BUFF)
    msg = data.decode('ASCII')
            
    s.close() #Connection closure

    time.sleep(t_ret)

    if 'Error' in msg:
        raise ValueError(msg)
    else:
        print('Instrument ' + msg[1:] + ' opened on ' + IP)
        return int(msg)

def write(IP: str, PORT: int, InstID: int, command: str) -> None:
    """To send SCPI commands without waiting for an answer.

    Args:
        IP: Gateway's IP
        PORT: TCP port
        InstID: Integer identifier the Gateway associated to the instrument when it was opened with :code:`open_inst`
        command: SCPI command to send to the Gateway
    """
    #Creating connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print('Socket creation error:')
        print(err)
        sys.exit()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((IP, PORT))
    #print('Socket created')

    #The header is the instrument ID, the data is the SCPI command
    msg = str(InstID) + command 
    data = msg.encode('ASCII') 
    s.send(data) 

    s.close() #Close connection

    time.sleep(t_ret)

def query(IP: str, PORT: int, InstID: int, command: str) -> str:
    """To send SCPI commands and wait for an answer

    Args:
        IP: Gateway's IP
        PORT: TCP port
        InstID: Integer identifier the Gateway associated to the instrument when it was opened with :code:`open_inst`
        command: SCPI command to send to the Gateway
    
    Returns:
        The string answered by the instrumentation when sending the selected SCPI command.
    """

    #Creating connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print('Socket creation error:')
        print(err)
        sys.exit()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((IP, PORT)) 
    #print('Socket created')

    #The header is the instrument ID, the data is the SCPI command
    msg = str(InstID) + command 
    data = msg.encode('ASCII')
    s.send(data)

    time.sleep(t_ret) #It seems to freeze if this doesn't goes here
    del(msg)

    #Receiving the answer
    data = s.recv(BUFF)
    msg = data.decode('ASCII')
            
    s.close() #Connection closure

    time.sleep(t_ret)
    
    #Maybe the GW answers an error, this handles it
    if 'Error' in msg:
        raise ValueError(msg)
    else:
        return msg

def close_term(IP: str, PORT: int) -> None:
    """This reboots the gateway
    
    Args:
        IP: Gateway's IP
        PORT: TCP port
    """
    #Creating connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print('Socket creation error:')
        print(err)
        sys.exit()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((IP, PORT)) 
    #print('Socket created')

    msg = '1' + 'close' 
    data = msg.encode('ASCII') 
    s.send(data)

    s.close() #Connection close

    print('Terminal ' + IP + ' closed.')
    time.sleep(t_ret)

def send_program(IP: str, PORT: int, NAME_IN: str, *NAMEs_OUT: str) -> None:
    """Can be used to send an entire program to the Gateway.

    This enables the standalone mode, where all the measurement orders
    are coded in a program that is sent to the Gateway and launched. The
    host waits for receiving the files with the results of the measurement.
    
    Args:
        IP: Gateway's IP
        PORT: TCP port
        NAME_IN: The name of the file with the program to be sent to the Gateway
        *NAMEs_OUT: Name(s) of the file(s) that are going to be generated by the NAME_IN program and sent to the host
    """
    
    #Creating connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print('Socket creation error:')
        print(err)
        sys.exit()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.connect((IP, PORT)) 
    #print('Socket created')

    #Sending the path of the input program
    #It assumes the GW to have a default Raspbian OS
    msg = 'p/home/pi/Desktop/' + NAME_IN
    data = msg.encode('ASCII')
    s.send(data) 

    time.sleep(t_ret)

    #Return the input path as a feedback
    data = s.recv(BUFF)
    print(data.decode('ASCII'))

    #Sending the number of output files
    msg = str(len(NAMEs_OUT))
    data = msg.encode('ASCII')
    s.send(data)

    #Return it as a feedback
    data = s.recv(BUFF)
    print(data.decode('ASCII'))

    fout=[]
    #Sending the output paths and opening this
    #files locally for their future writing
    for name in NAMEs_OUT:
        fout.append(open(name, 'wb'))
        msg = '/home/pi/Desktop/' + name
        data = msg.encode('ASCII')
        s.send(data)
        time.sleep(t_ret)

        #Return it as a feedback
        data = s.recv(BUFF)
        print(data.decode('ASCII'))
        time.sleep(t_ret)

    time.sleep(1)

    #Sending the input program size
    lenght = fillp2(NAME_IN)
    print(lenght)
    msg = str(lenght)
    data = msg.encode('ASCII')
    s.send(data)

    #Return it as a feedback
    data = s.recv(BUFF)
    print(data.decode('ASCII'))

    time.sleep(1)

    #Sending input program
    f = open (NAME_IN, "rb")
    s.send(f.read(lenght))
    f.close()

    #Return it as a feedback
    data = s.recv(BUFF)
    print(data.decode('ASCII'))

    time.sleep(1)

    #Receiving output files
    for k in range(len(NAMEs_OUT)):

        msg = 'PC: ready to receive file size'
        data = msg.encode('ASCII')
        s.send(data)

        #Receiving file size
        data = s.recv(512)
        msg = data.decode('ASCII')
        print(msg)
        n_paq = int(float(msg))
        print('Number of packets to receive ' + str(n_paq))

        msg = 'PC: Ready to receive file'
        data = msg.encode('ASCII')
        s.send(data)

        for h in range(n_paq):
            data = s.recv(512)
            #print(data)
            fout[k].write(data)
        fout[k].close()

        time.sleep(1)

    s.close()