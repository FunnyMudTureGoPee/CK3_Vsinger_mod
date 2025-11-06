import os
inputpath = "PATH TO MOD EDITED animation"
outputpath = "PATH TO YOUR Anime Core Lib/PATCH FILE"

workpath = "gfx/portraits/portrait_animations"

code = "utf_8_sig"    # utf8-bom, paradox coding
newgroup = '''\t\thm_idle = {
\t\t\tanimation = { head = "dead" torso = "dead" }
\t\t\tweight = {
\t\t\t\tbase = 0
\t\t\t\tmodifier = {
\t\t\t\t\tadd = 32767
\t\t\t\t\twaifu_portrait_trigger = yes
\t\t\t\t}
\t\t\t}
\t\t}
'''
modifier = '''\ttrigger = { waifu_portrait_trigger = no }\n'''

dead = False
with open(os.path.join(inputpath, workpath, 'animations.txt'), encoding=code) as input:
    with open(os.path.join(outputpath, workpath, 'animations.txt'), "w+", encoding=code) as output:
        for line in input:
            output.write(line)
            if line.strip('\n\r ') == 'dead = {':
                dead = True
            elif '\tdefault = {' == line.strip('\n\r ') and not dead:
                output.write(newgroup)
            elif 'portrait_modifier = {' in line:
                output.write(line.split('p')[0]+modifier)
            if dead and '}' in line:
                dead = False

fulltrigger = '''\ttrigger = { waifu_portrait_trigger = no }\n'''
modifier = '''\twaifu_portrait_trigger = no\n'''
entry = False
with open(os.path.join(inputpath, workpath, 'animations.modifierpack'), encoding=code) as input:
    with open(os.path.join(outputpath, workpath, 'animations.modifierpack'), "w+", encoding=code) as output:
        for line in input:
            output.write(line)
            if 'portrait_modifier = {' in line:
                entry = True
            elif entry:
                if 'trigger = {' in line:
                    output.write(line.split('t')[0]+modifier)
                else:
                    output.write(line.split('a')[0]+fulltrigger)
                entry = False
