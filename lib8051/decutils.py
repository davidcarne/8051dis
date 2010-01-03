class DictProxy(object):
	def __init__(self,**args):
		self.d = args
		return self.__dict__.update(args)

	def __repr__(self):
		return str(self.d)


def sb(x):
	if x >= 128:
		return x - 256
	return x