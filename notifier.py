from pync import Notifier
import os

def notify(text):
   Notifier.notify('VACCINE NOTIFIER', title=text, execute='say "Opening Cowin App"',open='https://selfregistration.cowin.gov.in/')
   os.system("afplay /System/Library/Sounds/Glass.aiff")
   os.system("say 'Coawin vaccines found'")
