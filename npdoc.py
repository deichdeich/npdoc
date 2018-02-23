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
import requests
from bs4 import BeautifulSoup
import os

def npbr(func):
    webbrowser.open_new_tab('https://docs.scipy.org/doc/numpy/reference/generated/numpy.{}.html'.format(func))    

def npd(func, nl = None, browser = None):

    if '.' in func:
        lib, fun = func.split('.')
    else:
        fun = func
        
    if browser == 'br':
        npbr(func)
        
    else:
        doc_url = 'https://docs.scipy.org/doc/numpy/reference/generated/numpy.{}.html'.format(func)
        doc_content = requests.get(doc_url).content
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
            raw = requests.get(raw_url, stream = True)
            func_def = '{}('.format(fun)
            function = 0
            quotes = 0
            printables = []
            for i in raw.iter_lines():
                i = str(i)[2:-1]
                if func_def in i:
                    function = 1
                if '\"\"\"' in i and function == 1:
                    quotes += 1
                if function == 1 and quotes < 2 and '\"\"\"' not in i:
                    printables.append(i)
                    
                    
            if nl == None:
            	nl = len(printables)
            
            print_range = nl
            if print_range < 0:
                printables = printables[print_range:]
            elif print_range >= 0:
                printables = printables[:print_range]
            else:
                printables = printables
            
            print('\n'.join(printables))
