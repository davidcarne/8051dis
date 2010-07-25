class DictProxy(object):
	def __init__(self,**args):
		if "length" in args and "dests" in args and "pc" in args:
			for x in args["dests"]:
				if x > args["pc"] and x < args["pc"] + args["length"]:
					print "INVALID DEST!!!"
					exit(1)
		self.d = args
		return self.__dict__.update(args)

	def __repr__(self):
		return str(self.d)


def sb(x):
	if x >= 128:
		return x - 256
	return x
