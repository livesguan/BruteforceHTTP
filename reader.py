from itertools import islice

class Reader(object):
  def __init__(self, file):
    if type(file) is str:
      self.file = open(file)
    else:
      self.file = file
  def read(self, start, stop):
    return islice(self.file, start, stop)