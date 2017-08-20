"""
Author: Alex Deich
Date: August, 2017

Utility to read NumPy documentation in an IPython notebook.

Usage:

>> import npdoc

>> npd('linalg.tensorinv')

>> Compute the 'inverse' of an N-dimensional array.

   The result is an inverse for `a` relative to the tensordot operation
   ``tensordot(a, b, ind)``, i. e., up to floating-point accuracy,
   ``tensordot(tensorinv(a), a, ind)`` is the "identity" tensor for the
   tensordot operation...
    

You can also add the nl parameter to print the first x lines (if x > 0)
or the last x lines (if x is < 0).  Behold:

>> npd('linalg.tensorinv', nl = 4)

>> Compute the 'inverse' of an N-dimensional array.

    The result is an inverse for `a` relative to the tensordot operation
    ``tensordot(a, b, ind)``, i. e., up to floating-point accuracy,

OR

>> npd('linalg.tensorinv', nl = -4)

>> b = np.random.randn(24)
   np.allclose(np.tensordot(ainv, b, 1), np.linalg.tensorsolve(a, b))
   True
"""

import webbrowser
import urllib2
from bs4 import BeautifulSoup
import os


# iterator to evaluate a given string line-by-line
# by Alex Martelli from a stack overflow comment,
# https://stackoverflow.com/questions/3054604/iterate-over-the-lines-of-a-string
def linebyline(string):
    retval = ''
    for char in string:
        retval += char if not char == '\n' else ''
        if char == '\n':
            yield retval
            retval = ''
    if retval:
        yield retval

def npbr(func):
    webbrowser.open_new_tab('https://docs.scipy.org/doc/numpy/reference/generated/numpy.{}.html'.format(func))    

def npd(func, nl = None, browser = None):

    if '.' in func:
        lib, fun = func.split('.')
    else:
        fun = func
        
    if browser == True:
        npbr(func)
        
    else:
        doc_url = 'https://docs.scipy.org/doc/numpy/reference/generated/numpy.{}.html'.format(func)
        doc_content = urllib2.urlopen(doc_url).read()
        doc_soup = BeautifulSoup(doc_content, 'html.parser')
        
        links = doc_soup.find_all('a')
        source_url = None
        
        for link in links:
            if link.text == '[source]':
                source_url = link
        
        if source_url == None:
            # for the base numpy functions like np.arange, there is no "[source]"
            # link listed on the documentation page, and the naming conventions
            # for the github isn't as straightforward, so I just open the browser
            # at that point.
            print('Couldn\'t find an easy source... just gonna open the webpage')
            npbr(func)
        
        else:   
            # look for the URL to the NumPy function source on GitHub
            source_url = doc_soup.find("a", class_= "reference external" ).get('href')
            
            # edit the URL to go to the raw source.
            raw_url = source_url.replace('blob', 'raw')  
            raw = urllib2.urlopen(raw_url).read()
            
            func_def = 'def {}'.format(fun)
            function = 0
            quotes = 0
            printables = []
            for i in linebyline(raw):
                if func_def in i:
                    function = 1
                if '\"\"\"' in i and function == 1:
                    quotes += 1
                if function == 1 and quotes < 2 and func_def not in i and '\"\"\"' not in i:
                    printables.append(i)
            
            print_range = nl
            
            if print_range < 0:
                printables = printables[print_range:]
            elif print_range >= 0:
                printables = printables[:print_range]
            else:
                printables = printables
            
            print('\n'.join(printables))
            
