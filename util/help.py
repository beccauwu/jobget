# class TextUtils:
#     """
#     Class for text formatting
#     """
#     def __init__(self, text):
#         self.text = text
#         self.styles = {
#             'bold': '1',
#             'underline': '4',
#             'blink': '5',
#             'reverse': '7',
#             'concealed': '8',
#             'black': '30',
#             'red': '31',
#             'green': '32',
#             'yellow': '33',
#             'blue': '34',
#             'magenta': '35',
#             'cyan': '36',
#             'white': '37',
#             'on_black': '40',
#             'on_red': '41',
#             'on_green': '42',
#             'on_yellow': '43',
#             'on_blue': '44',
#             'on_magenta': '45',
#             'on_cyan': '46',
#             'on_white': '47',
#         }
#         self.style_count = 1
#         self.start = '\033['
#         self.chosens = []
#     def end(self):
#         start = '\033['
#         for i in range(self.style_count):
#             start += +
#     def bold(self):
#         return "\033[1m" + self.text + "\033[0m"

#     def underline(self):
#         return "\033[4m" + self.text + "\033[0m"

#     def red(self):
#         return "\033[1;31m" + self.text + "\033[0m"

#     def green(self):
#         return "\033[1;32m" + self.text + "\033[0m"

#     def yellow(self):
#         return "\033[1;33m" + self.text + "\033[0m"

#     def blue(self):
#         return "\033[1;34m" + self.text + "\033[0m"

#     def magenta(self):
#         return "\033[1;35m" + self.text + "\033[0m"

#     def cyan(self):
#         return "\033[1;36m" + self.text + "\033[0m"

#     def white(self):
#         return "\033[1;37m" + self.text + "\033[0m"
def print_all_opts():
    """
    Help text that displays all the options and their descriptions
    """
    return print("""
    \033[1;35m      ___       ___                   __
         |   |     |   |                 |  |
         |   |     |   |                 |  |
         |   |     |   |               __|  |___ 
    __   |   | ___ |   |___  ______  __\_    ___/   
   |  \__/   |/ _ \|   _   \/  _   \/ _ \|  |
   \         | (_) |  (_)  || (_)  |  __/|  |__/\   
    \________/\___/\_______/\___   |\___|\______/    
                            __  |  |      
                           /  \_|  |
                           \______/   \033[0m
                        
    \033[1;36musage:\033[0;0m jobget.py \033[1;32m[options]\033[0m
    \033[1;36moptions:\033[0;0m

    \033[1;35m---short-------long--------------description----\033[0;0m
    -h         | --help            | print this help
    -q \033[1;32m<query>\033[0m | --query=\033[1;32m<query>\033[0m   | search for \033[1;32m<query>\033[0m \033[0;31m(required)\033[0;0m
    -l \033[1;32m<lang>\033[0m  | --lang=\033[1;32m<lang>\033[0m     | search for \033[1;32m<lang>\033[0m  \033[0;33m(sv, en)\033[0;0m
    -f \033[1;32m<csv>\033[0m   | --filter=\033[1;32m<csv>\033[0m    | filter results by \033[1;32m<csv>\033[0;0m
    -e         | --email           | search for ads with email
    -r         | --remote          | search for remote jobs
    -s         | --send            | send applications to ads with email
    -w         | --write           | write results from different stages to separate files
    \033[0;35m------------------------------------------------\033[0;0m
    """)