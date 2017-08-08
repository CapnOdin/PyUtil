
import traceback, os, sys, time

def add_to_pypath():
	import os, sys, inspect
	
	 # for parent dir
	cmd_folder = os.path.realpath(os.path.abspath(os.path.pardir))
	if cmd_folder not in sys.path:
		sys.path.insert(0, cmd_folder)
	
	 # realpath() will make your script run, even if you symlink it :)
	cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
	if cmd_folder not in sys.path:
		sys.path.insert(0, cmd_folder)
	
	 # use this if you want to include modules from a subfolder
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"subfolder")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
		
		

def isInt(v):
	v = str(v).strip()
	return v=='0' or (v if v.find('..') > -1 else v.lstrip('-+').rstrip('0').rstrip('.')).isdigit()


def print_object(obj, printDictData = False):
	if(isinstance(obj, dict)):
		elements = sorted(obj.keys())
	else:
		elements = obj
	for element in elements:
		print(element, end = "")
		if(printDictData):
			print(" : " + str(obj[element]), end = "")
		print()


def full_stack():
		import traceback, sys
		exc = sys.exc_info()[0]
		stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
		if(exc != None):  # i.e. if an exception is present
			del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
		trc = 'Traceback (most recent call last):\n'
		stackstr = trc + "".join(traceback.format_list(stack))
		if(exc != None):
			stackstr += '  ' + traceback.format_exc().lstrip(trc)
		print(stackstr)


def str_in_Error(string, Error, fun, *args):
	try:
		fun(*args)
	except Error as e:
		if(string in str(e)):
			return True
	return False


def getScriptPath():
	return os.path.dirname(os.path.realpath(sys.argv[0]))


def print_exception(etype, value, tb, limit=None, file=None, chain=True):
	f = open("log.txt", "a")
	f.write(time.strftime("[%d-%m-%y - %H:%M:%S]") + "\n")
	if file is None:
		file = sys.stderr
	for line in traceback.TracebackException(type(value), value, tb, limit=limit).format(chain=chain):
		print(line, file=file, end="")
		f.write(line)
	f.write("\n")

traceback.print_exception = print_exception


