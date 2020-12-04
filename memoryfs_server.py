import pickle, logging, sys

from memoryfs_client import BLOCK_SIZE, TOTAL_NUM_BLOCKS, RSM_LOCKED

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
  rpc_paths = ('/RPC2',)

class DiskBlocks():
  def __init__(self):
    # This class stores the raw block array
    self.block = []                                            
    # Initialize raw blocks 
    for i in range (0, TOTAL_NUM_BLOCKS):
      putdata = bytearray(BLOCK_SIZE)
      self.block.insert(i,putdata)

if __name__ == "__main__":

  if len(sys.argv) > 2:
    print("Only one command-line argument to specify port # allowed")
    quit()
  else:
    portNum = int(sys.argv[1])

  RawBlocks = DiskBlocks()

  # Create server
  server = SimpleXMLRPCServer(("localhost", portNum), requestHandler=RequestHandler) 

  def Get(block_number):
    result = RawBlocks.block[block_number]
    return result

  server.register_function(Get)

  def Put(block_number, data):
    RawBlocks.block[block_number] = data
    return 0

  server.register_function(Put)

  def RSM(block_number):
    result = RawBlocks.block[block_number]
    RawBlocks.block[block_number] = RSM_LOCKED
    # RawBlocks.block[block_number] = bytearray(RSM_LOCKED.ljust(BLOCK_SIZE,b'\x01'))
    return result

  server.register_function(RSM)

  # Run the server's main loop
  server.serve_forever()

