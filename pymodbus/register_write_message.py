'''
Register Writing Request/Response Messages
-------------------------------------------
'''

from pymodbus.pdu import ModbusRequest
from pymodbus.pdu import ModbusResponse
from pymodbus.pdu import ModbusExceptions as merror
import struct

class WriteSingleRegisterRequest(ModbusRequest):
    '''
    This function code is used to write a single holding register in a
    remote device.

    The Request PDU specifies the address of the register to
    be written. Registers are addressed starting at zero. Therefore register
    numbered 1 is addressed as 0.
    '''
    function_code = 6

    def __init__(self, address=None, value=None):
        ''' Initializes a new instance
        @param address The address to start writing add
        @param value The values to write
        '''
        ModbusRequest.__init__(self)
        self.address = address
        self.value = value

    def encode(self):
        ''' Encode a write single register packet packet request
        @return The encoded packet
        '''
        ret = struct.pack('>HH', self.address, self.value)
        return ret

    def decode(self, data):
        ''' Decode a write single register packet packet request
        @param data The request to decode
        '''
        self.address, self.value = struct.unpack('>HH', data)

    def execute(self, context):
        ''' Run a write single register request against a datastore
        @param context The datastore to request from
        @return A WriteSingleRegisterResponse or a ModbusException
        if there were any errors
        '''
        if not (0 <= self.value <= 0xffff):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address):
            return self.doException(merror.IllegalAddress)
        context.setValues(self.function_code, self.address, [self.value])
        values = context.getValues(self.function_code, self.address)
        return WriteSingleRegisterResponse(self.address, values[0])

    def __str__(self):
        ''' Returns a string representation of the instance
        @return A string representation of the instance
        '''
        return "WriteRegisterRequest %d => %d" % (self.address, self.value)

class WriteSingleRegisterResponse(ModbusResponse):
    '''
    The normal response is an echo of the request, returned after the
    register contents have been written.
    '''
    function_code = 6

    def __init__(self, address=None, value=None):
        ''' Initializes a new instance
        @param address The address to start writing add
        @param value The values to write
        '''
        ModbusResponse.__init__(self)
        self.address = address
        self.value = value

    def encode(self):
        ''' Encode a write single register packet packet request
        @return The encoded packet
        '''
        ret = struct.pack('>HH', self.address, self.value)
        return ret

    def decode(self, data):
        ''' Decode a write single register packet packet request
        @param data The request to decode
        '''
        self.address, self.value = struct.unpack('>HH', data)

    def __str__(self):
        ''' Returns a string representation of the instance
        @return A string representation of the instance
        '''
        return "WriteRegisterResponse %d => %d" % (self.address, self.value)

#---------------------------------------------------------------------------#
# Write Multiple Registers
#---------------------------------------------------------------------------#

class WriteMultipleRegistersRequest(ModbusRequest):
    '''
    This function code is used to write a block of contiguous registers (1
    to approx. 120 registers) in a remote device.

    The requested written values are specified in the request data field.
    Data is packed as two bytes per register.
    '''
    function_code = 16

    def __init__(self, address=None, count=None):
        ''' Initializes a new instance
        @param address The address to start writing to
        @param count The number of registers to write to
        '''
        ModbusRequest.__init__(self)
        self.address = address
        if count != None and count > 0:
            self.registers = [0] * count
        else: self.registers = []

    def encode(self):
        ''' Encode a write single register packet packet request
        @return The encoded packet
        '''
        count = len(self.registers)
        ret = struct.pack('>HHB', self.address, count, count*2)
        for reg in self.registers:
            ret += struct.pack('>H', reg)
        return ret

    def decode(self, data):
        ''' Decode a write single register packet packet request
        @param data The request to decode
        '''
        self.address, count, self.byte_count = struct.unpack('>HHB', data[:5])
        for i in range(5, count*2+5, 2):
            self.registers.append(struct.unpack('>H', data[i:i+2])[0])

    def execute(self, context):
        ''' Run a write single register request against a datastore
        @param context The datastore to request from
        '''
        count = len(self.registers)
        if not (1 <= count <= 0x07b):
            return self.doException(merror.IllegalValue)
        if (self.byte_count != count * 2):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, count):
            return self.doException(merror.IllegalAddress)
        context.setValues(self.function_code, self.address, self.registers)
        return WriteMultipleRegistersResponse(self.address, count)

    def __str__(self):
        ''' Returns a string representation of the instance
        @return A string representation of the instance
        '''
        return "WriteNRegisterRequest %d => " % self.address, self.registers

class WriteMultipleRegistersResponse(ModbusResponse):
    '''
    "The normal response returns the function code, starting address, and
    quantity of registers written.
    '''
    function_code = 16

    def __init__(self, address=None, count=None):
        ''' Initializes a new instance
        @param address The address to start writing to
        @param count The number of registers to write to
        '''
        ModbusResponse.__init__(self)
        self.address = address
        self.count = count

    def encode(self):
        ''' Encode a write single register packet packet request
        @return The encoded packet
        '''
        ret = struct.pack('>HH', self.address, self.count)
        return ret

    def decode(self, data):
        ''' Decode a write single register packet packet request
        @param data The request to decode
        '''
        self.address, self.count = struct.unpack('>HH', data)

    def __str__(self):
        ''' Returns a string representation of the instance
        @return A string representation of the instance
        '''
        return "WriteNRegisterResponse (%d,%d)" % (self.address, self.count)

#---------------------------------------------------------------------------# 
# Exported symbols
#---------------------------------------------------------------------------# 
__all__ = [
    "WriteSingleRegisterRequest", "WriteSingleRegisterResponse",
    "WriteMultipleRegistersRequest", "WriteMultipleRegistersResponse",
]