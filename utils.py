import hashlib
import math

hex2bin = {
    '0': "0000",
    '1': "0001",
    '2': "0010",
    '3': "0011",
    '4': "0100",
    '5': "0101",
    '6': "0110",
    '7': "0111",
    '8': "1000",
    '9': "1001",
    'a': "1010",
    'b': "1011",
    'c': "1100",
    'd': "1101",
    'e': "1110",
    'f': "1111", 
}

def convert_to_bin(hex):
  result = ""
  for c in hex:
    result = result + hex2bin[c]
  return result

def get_header_string (header, nonce):
  return (header["HASH_PREV_BLOCK_KEY"] + header["HASH_MERKLE_ROOT_KEY"]+
              header["TIME_KEY"] + str(nonce))

def hash_header(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

def guarante_difficulty(hashed_header, difficulty):
  binary_hash = convert_to_bin(hashed_header)
  for c in binary_hash[: difficulty ] :
    if c == '1':
      return False
  return True

def pow(header, difficulty):
  nonce = 0
  while(True):
    print(nonce)
    hashed_header = hash_header(get_header_string(header, nonce))
    if(guarante_difficulty(hashed_header[: math.ceil(difficulty/4)], difficulty)):
      header["NONCE_KEY"] = str(nonce)
      return header, hashed_header
    nonce = nonce + 1