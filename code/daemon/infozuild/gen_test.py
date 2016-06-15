'''
Used to verify the new sendscript and the old sendscript behave the same.
'''
import copy
import logging

from infozuild import sendscript, sendscript_new


logging.basicConfig(level=logging.DEBUG)

page_lines = [
    'Dit is een testpagina',
    'Met een aantal letters',
    'Heel interessant allemaal',
    '',
    'Oeps de rest is leeg'
    ]
page2_lines = [
    'Wederom een testpagina',
    '%y %M %D %H %m %S %R',
    'Wat spannend weer',
    '',
    '',
    'Als dat maar goed gaat'
    ]

old_style = {
    'pages': [{
        'lines': page_lines,
        'time': 1000
        },
        {
            'lines': page2_lines,
            'time': 1000
            }]
    }
old_cts = sendscript.build_controlstring(old_style, 0)

new_style = sendscript_new.Rotation()
page = sendscript_new.Page(page_lines)
page.scrolling = False
page.fading = False
page.duration = 1000
#page.schedular = None
page.blinkspeed = 0
page.brightness = 0
new_style.pages.append(page)
page2 = copy.deepcopy(page)
page2.lines = page2_lines
new_style.pages.append(page2)
new_cts = new_style.to_controlstring()



