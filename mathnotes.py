#!/usr/bin/python

from os import listdir,makedirs
from os.path import isfile,isdir,join,splitext,exists
import re

import chevron
import markdown2




find_math_envs = r'(\$[^\$]+\$)|(\$\$[^\$]+\$\$)'
to_escape = r'(\\|`|\*|\_|{|}|\[|\]|\(|\)|#|\+|-|\.|!)'
escape = r'\\\1'
def escapelatex(text):
    out = ''
    i = 0
    envs = re.findall(find_math_envs, text)
    for env in envs:
        envstr = env[0] if env[0] else env[1]
        j = text.find(envstr, i)
        out += text[i:j]
        out += re.sub(to_escape, escape, envstr)
        i = j + len(envstr)
    return out + text[i:]





def extracttitle(path):
    with open(path,'r') as f:
        firstline = f.readline()
        if len(firstline) == 0 or firstline[0] != '#': return ''
        return firstline[1:].lstrip().rstrip()
    return ''

def parseindex_recur(basedir, parentdir, curdir):
    p = join(parentdir,curdir)
    node = {'isfolder':True, 'isfile':False, 'title':curdir, 
            'path': join(basedir,p), 'output':p, 'children':[]}
    if curdir:
        titlefile = join(basedir,p,'_title')
        if exists(titlefile):
            with open(titlefile, 'r') as f: node['title'] = f.read()
    for f in sorted(listdir(join(basedir,p))):
        if isdir(join(basedir,p,f)):
            node['children'].append(parseindex_recur(basedir,p,f))
        if isfile(join(basedir,p,f)) and splitext(f)[1] == '.mmd':
            foundtitle = extracttitle(join(basedir,p,f))
            outfile = splitext(f)[0] + '.html'
            article = {'isfolder':False, 'isfile':True, 
                    'title':foundtitle if foundtitle else splitext(f)[0], 
                    'path':join(basedir,p,f), 'output':join(p,outfile), 'children':[]}
            node['children'].append(article)
    return node







def generateindex(index, templatepath):
    args = {
        'partials_path': templatepath,
        'partials_ext': 'mustache.html',
        'template': '{{>main}}',
        'data': { 'index': index }
    } 
    return chevron.render(**args)



def generatearticle(templatepath, node):
    if not node['isfile']: return
    content = escapelatex(open(node['path'],'r').read())
    args = {
        'partials_path': templatepath,
        'partials_ext': 'mustache.html',
        'template': '{{>article}}',
        'data': { 'title': node['title'], 'content': markdown2.markdown(content) }
    }
    return chevron.render(**args)



def create_recur(outpath, templatepath, node):
    if node['isfile']:
        with open(join(outpath,node['output']), 'w') as f: 
            f.write(generatearticle(templatepath, node))
    elif node['isfolder']:
        makedirs(join(outpath,node['output']), exist_ok=True)

    for child in node['children']: 
        create_recur(outpath, templatepath, child)

def create(index, templatepath, outpath):
    makedirs(outpath, exist_ok=True)
    with open(join(outpath, 'index.html'), 'w') as f:
        f.write(generateindex(index, templatepath))
    for child in index['children']:
        makedirs(join(outpath,child['output']), exist_ok=True)
        create_recur(outpath, templatepath, child)




create(parseindex_recur('./articles','',''), './templates', './build')
