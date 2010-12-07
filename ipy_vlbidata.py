
""" User configuration file for IPython

This is a more flexible and safe way to configure ipython than *rc files
(ipythonrc, ipythonrc-pysh etc.)

This file is always imported on ipython startup. You can import the
ipython extensions you need here (see IPython/Extensions directory).

Feel free to edit this file to customize your ipython experience.

Note that as such this file does nothing, for backwards compatibility.
Consult e.g. file 'ipy_profile_sh.py' for an example of the things 
you can do here.

See http://ipython.scipy.org/moin/IpythonExtensionApi for detailed
description on what you could do here.
"""


# Most of your config files and extensions will probably start with this import
import IPython.ipapi as ipapi
ip = ipapi.get()
o = ip.options
    

def main():   

    # Set banner
    o.banner += 'Starting in VLBIDATA mode...\n'

    # Import the vlbidata tools
    o.autoexec.append("import vlbidata")
    o.autoexec.append("from vlbidata import *")

    # Expose useful commands
    ip.expose_magic('day', day)
    ip.expose_magic('only', only)

    
# some config helper functions you can use 
def day(self, arg):
    ip = self.api
    ip.ex("all = process_day(%s)" % ', '.join(arg.split()))

def only(self, arg):
    ip = self.api
    ip.ex("final = filter(all, \"%s\")" % arg)


main()
