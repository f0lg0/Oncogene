import os 
import threading

scriptpath = "C:/Users/..." # MODIFY ME
exepath = "C:/Users/..." # MODIFY ME
backupexe = "C:/Users/..." # MODIFY ME

def front():
    os.startfile(exepath)

def back():
    os.startfile(scriptpath)
    

def main():
    os.startfile(backupexe)

    bThread = threading.Thread(target = back)
    bThread.daemon = True
    bThread.start()

    front()


if __name__ == "__main__":
    main()