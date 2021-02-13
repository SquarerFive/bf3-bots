import os

os.system('quasar build')
os.system('cd .. && cd bin && vuicc.exe "H:/Repositories/bf3-bots/navigation/dist/spa" "../bf3_bots_mod/ui.vuic"')