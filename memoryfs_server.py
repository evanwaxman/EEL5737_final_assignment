import pickle, logging, sys, hashlib

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
    self.cs_block = []                                          
    # Initialize raw blocks 
    for i in range (0, TOTAL_NUM_BLOCKS):
      putdata = bytearray(BLOCK_SIZE)
      value_string = str(putdata)
      value_byte = bytes(value_string, 'utf-8')
      cs = hashlib.md5(value_byte).digest()
      self.block.insert(i,putdata)
      self.cs_block.insert(i,cs)

if __name__ == "__main__":

  if len(sys.argv) > 3:
    print("Command-line arguments should be: <port_number> <optional: corrupter_block>")
    quit()
  else:
    portNum = int(sys.argv[1])
    if len(sys.argv) == 3:
      damaged_block_flag = 1
      damaged_block_number = int(sys.argv[2])
    else:
      damaged_block_flag = 0

  RawBlocks = DiskBlocks()

  # Create server
  server = SimpleXMLRPCServer(("localhost", portNum), requestHandler=RequestHandler) 

  def Get(block_number):
    result = RawBlocks.block[block_number]
    value_string = str(result)
    value_byte = bytes(value_string, 'utf-8')
    new_cs = hashlib.md5(value_byte).digest()
    old_cs = RawBlocks.cs_block[block_number]
    if new_cs != old_cs:
      print("ERROR: CHECKSUM MISMATCH")
      return -1
    elif damaged_block_flag:
      if block_number == damaged_block_number:
        print("ERROR: CHECKSUM MISMATCH")
        return -1

    return result

  server.register_function(Get)

  def Put(block_number, data):
    RawBlocks.block[block_number] = data
    value_string = str(data)
    value_byte = bytes(value_string, 'utf-8')
    new_cs = hashlib.md5(value_byte).digest()
    RawBlocks.cs_block[block_number] = new_cs
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

