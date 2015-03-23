__author__ = 'f.forti'


DEBUG = True

class Error(Exception):
	"""
	classe base per l'eccezioni.
	DA EREDITARE IN OGNI ECCEZIONE CREATA.
	"""

	def __init__(self, msg):
		"""

		:param msg:
		:return:
		"""
		msg = "--->ATTENTION! " + msg
		super(Error, self).__init__(msg)
		self.msg = msg

class constructionError(Error):
	def __init__(self, className):
		msg = "There is an error in the construction of the " + str(className) + " class."
		super(Error, self).__init__(msg)
		self.className = className

def toStr(s):
	if type(s) is list:
		return "[ %s ]" % (reduce(lambda x, y: str(x)+", "+str(y), s))
	elif type(s) is dict:
		string = "{ "
		for k in s:
			string += "%s: %s" % (toStr(k), toStr(s[k]))
		string += " }"
		return string
	else:
		return str(s)

def dbg(s, *args):
	pref = "----->DEBUG: "
	if not DEBUG:
		return False
	if len(args) > 0:
		if len(args) != s.count("%s"):
			print pref+toStr(s)+toStr([toStr(arg) for arg in args])
		else:
			print pref+toStr(s) % tuple([toStr(arg) for arg in args])
	else:
		print pref+toStr(s)

def logger(func):
	pref = "----->LOGGER: "
	def inner(*args, **kwargs): #1
		dbg("%s Function was %s", pref, str(func.__name__))
		dbg("%s Arguments were: %s, %s", pref, *args, **kwargs)
		returned = func(*args, **kwargs)
		dbg("%s returned was: %s", pref, returned)
		return returned
	return inner