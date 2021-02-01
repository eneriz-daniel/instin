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

def sen_msg(host: socket.socket, msg: str) -> None:
    data = msg.encode('ASCII')
    host.send(data)

def receive_msg(host):
    data = host.recv(BUFF)
    mensaje = data.decode('ASCII')

    return mensaje

def launch_program(host, path_in):
    #Receiving program to run
    fin = open(path_in,'wb')
    
    n_paths_out = receive_msg(host)
    print('Nuemro de archivos de salida: '+n_paths_out)
    sen_msg(host, 'Archivos de salida '+ n_paths_out)
    
    paths_out = []
    
    for pout in range(int(n_paths_out)):
        paths_out.append(receive_msg(host))
        sen_msg(host, 'Archivo de salida '+str(pout)+':'+paths_out[pout])
    
    #Recibimos el tamaño del trograma de salida
    fin_lengh = receive_msg(host)
    print(int(fin_lengh))
    print('Tamaño programa entrada ' + fin_lengh)
    
    sen_msg(host, 'El tamano del programa de entrada es '+fin_lengh)

    print('Recibimos el progama a ejecutar')
    n_paq = int(fin_lengh)/512
    print(n_paq)
    for k in range(int(n_paq)):
        data = host.recv(512)
        print(data)
        fin.write(data)
    fin.close()

    sen_msg(host, 'Programa recibido')
    
    print('Programa iniciandose')
    os.system('sudo python3 '+path_in) #Lanzamos el programa
    print('Fin de ejecución del programa, devolviendo archivos de salida')
    
    for pout in range(int(n_paths_out)):
        print(receive_msg(host))
        
        leng = fillp2(paths_out[pout])
        print('Tamaño programa salida ' + str(pout) + ': '+ str(leng))
        
        #Envaimos el numero de paquetes de 512 b de los programas de salida
        n_paq = int(leng)/512.0
        sen_msg(host, str(n_paq))
        print(n_paq)
        
        file_out = open(paths_out[pout],'rb')
        
        print(receive_msg(host))

        for k in range(int(n_paq)):
            data = file_out.read(512)
            print(data)
            host.send(data)
            sleep(0.2)
        
        file_out.close()
        
        sleep(1)
        

    print('Datos enviados')


rm=pyvisa.ResourceManager('@py') #Añadir '@py' al pasar a Linux

#Creamos el objeto socket:
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Nos permite usar el mismo puerto
try:
    s.bind(('', port))
except socket.error as err:
    print('Bind failed')
    print(err)
s.listen(N_links) #Limitamos el número de clientes que se pueden conectar al servidor
print('Socket awaiting messages')

(conn, addr) = s.accept() #Nos conectamos
print('Connected to ' + str(addr))
msg = receive_msg(conn)
os.system('sudo date ' + msg) #Ponemos en hora la Raspi Quitar el comentario al pasar a linux
conn.close()

print('Inicio programa')

inst = []
inst.append(0)

while True:
    (conn, addr) = s.accept() #Nos conectamos
    print('Connected to ' + str(addr))
    
    msg = receive_msg(conn) #Leemos el mensaje
    print("Mensaje recibido: "+msg)
    
    if msg[0] == 'p':
        sen_msg(conn, 'Abriendo '+msg[1:])
        launch_program(conn, msg[1:])
    else:
        n_inst = int(msg[0])
        msg = msg[1:]

        if n_inst == 0: #Si pasamos un cero es porque abrimos nuevo intrumento
            print("Intentando abrir un instrumento...")
            try:
                inst.append(rm.open_resource(msg))
                sen_msg(conn, str(len(inst)-1)) #devolvemos el ID que le asigna la RasPi al nuevo instruemnto
                print("Ok!\n")
            except IndexError:
                sen_msg(conn, "IndexError: VISA not correct")
                print('Error\n')
            except ValueError:
                sen_msg(conn, "ValueError: VISA not correct")
                print('Error\n')
            except pyvisa.errors.VisaIOError:
                sen_msg(conn, "VisaIOError: Insufficient location information or the requested device or resource is not present in the system.")
                print('Error\n')
            except:
                sen_msg(conn, "Unexpected Error")
                print('Error\n')
            
        elif '?' in msg: #Si el mensaje tiene ? es query
            print("Recibido query...")
            try:
                data = inst[n_inst].query(msg)
                sen_msg(conn, str(data))
                print("Ok!\n")
            except pyvisa.errors.VisaIOError:
                sen_msg(conn, 'VisaIOError: Visa communication error on query')
                print("Error\n")
            except:
                sen_msg(conn, 'Unexpected Error')
                print("Error\n")

        elif msg == 'close': #Si el mensaje es close apagamos
            conn.close()
            s.close()
            os.system('reboot')

        else: #Ya sólo nos queda que sea un write
            inst[n_inst].write(msg)

    conn.close()