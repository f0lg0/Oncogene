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

def banner():
    version = "0.6.0"
    githublink = "https://github.com/f0lg0/Oncogene"

    print("\n+--------------------------------------------------------------+\n")

    LOGO = [
        "|--- ONCOGENE ----|",
        " \---------------/ ",
        "  ~-_---------_-~  ",
        "     ~-_---_-~		",
        "        ~-_   		",
        "     _-~---~-_     ",
        "  _-~---------~-_  ",
        " /---------------\	",
        "|-----------------|"
    ]

    BANNER = [
        "       |",
        "       |   Welcome to Oncogene",
        f"       |   Version: {version}",
        "  |",
        f"  |   {githublink}",
        "       |",
        "       |   Written by: f0lg0",
        "  |",
        f"       |   {colors.FAIL}[!] Only for educational purposes",
    ]

    for llogo, lbanner in zip(LOGO, BANNER):
        print(colors.OKGREEN + colors.BOLD + llogo, colors.OKBLUE + colors.BOLD + lbanner)

    print(colors.ENDC)
    print("\n+--------------------------------------------------------------+")

