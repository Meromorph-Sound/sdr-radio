#!/usr/bin/python3

import xmlrpc.client
import re

class Client(object):

    def __init__(self,uri):
        self.proxy=xmlrpc.client.ServerProxy(uri)
        self.methods=[]
        self.getters=[]
        self.setters=[]
        self.load()
        
    def getVariableNames(self,prefix):
        names=[]
        regex=f'{prefix}\_(\S+)$'
        for m in self.methods:
            match=re.match(regex,m)
            if match : names.append(match.group(1))
        return names

    def load(self):
        m=self.proxy.system.listMethods()
        self.methods=[x for x in m if not x.startswith('system.')]
        self.getters=self.getVariableNames('get')
        self.setters=self.getVariableNames('set')

    def get(self,variable):
        if variable in self.getters:
            name=f'get_{variable}'
            method=getattr(self.proxy,name)
            return method()
        else:
            return None

    def set(self,variable,value):
        if variable in self.setters:
            name=f'set_{variable}'
            method=getattr(self.proxy,name)
            method(value)

    def __iter__(self):
        j=self.getters.copy()
        j.extend(self.setters)
        return iter(j)

c=Client('http://localhost:8000')
for n in c: print(n)
sr=c.get('samp_rate')
print(f'SR = {sr}')
c.set('amp',0.7)

