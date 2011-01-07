"""
Modbus Device Controller
-------------------------

These are the device management handlers.  They should be
maintained in the server context and the various methods
should be inserted in the correct locations.
"""
from itertools import izip
from pymodbus.interfaces import Singleton

#---------------------------------------------------------------------------#
# Network Access Control
#---------------------------------------------------------------------------#
class ModbusAccessControl(Singleton):
    '''
    This is a simple implementation of a Network Management System table.
    Its purpose is to control access to the server (if it is used).
    We assume that if an entry is in the table, it is allowed accesses to
    resources.  However, if the host does not appear in the table (all
    unknown hosts) its connection will simply be closed.

    Since it is a singleton, only one version can possible exist and all
    instances pull from here.
    '''
    __nmstable = [
            "127.0.0.1",
    ]

    def __iter__(self):
        ''' Iterater over the network access table

        :returns: An iterator of the network access table
        '''
        return self.__nmstable.__iter__()

    def add(self, host):
        ''' Add allowed host(s) from the NMS table

        :param host: The host to add
        '''
        if not isinstance(host, list):
            host = [host]
        for entry in host:
            if entry not in self.__nmstable:
                self.__nmstable.append(entry)

    def remove(self, host):
        ''' Remove allowed host(s) from the NMS table

        :param host: The host to remove
        '''
        if not isinstance(host, list):
            host = [host]
        for entry in host:
            if entry in self.__nmstable:
                self.__nmstable.remove(entry)

    def check(self, host):
        ''' Check if a host is allowed to access resources

        :param host: The host to check
        '''
        return host in self.__nmstable

#---------------------------------------------------------------------------#
# Device Information Control
#---------------------------------------------------------------------------#
class ModbusDeviceIdentification(object):
    '''
    This is used to supply the device identification
    for the readDeviceIdentification function

    For more information read section 6.21 of the modbus
    application protocol.
    '''
    __data = {
        0x00: '', # VendorName
        0x01: '', # ProductCode
        0x02: '', # MajorMinorRevision
        0x03: '', # VendorUrl
        0x04: '', # ProductName
        0x05: '', # ModelName
        0x06: '', # UserApplicationName
        0x07: '', # reserved
        0x08: '', # reserved
        # 0x80 -> 0xFF are private
    }

    def __init__(self, info=None):
        '''
        Initialize the datastore with the elements you need.
        (note acceptable range is [0x00-0x06,0x80-0xFF] inclusive)

        :param info: A dictionary of {int:string} of values
        '''
        if isinstance(info, dict):
            for key in info.keys():
                if (0x06 >= key >= 0x00) or (0x80 > key > 0x08):
                    self.__data[key] = info[key]

    def __iter__(self):
        ''' Iterater over the device information

        :returns: An iterator of the device information
        '''
        return self.__data.iteritems()

    def update(self, input):
        ''' Update the values of this identity
        using another identify as the value

        :param input: The value to copy values from
        '''
        self.__data.update(input)

    def __setitem__(self, key, value):
        ''' Wrapper used to access the device information

        :param key: The register to set
        :param value: The new value for referenced register
        '''
        if key not in [0x07, 0x08]:
            self.__data[key] = value

    def __getitem__(self, key):
        ''' Wrapper used to access the device information

        :param key: The register to read
        '''
        return self.__data.setdefault(key, '')

    def __str__(self):
        ''' Build a representation of the device

        :returns: A string representation of the device
        '''
        return "DeviceIdentity"

    #---------------------------------------------------------------------------#
    # Property access (and named to boot)
    #---------------------------------------------------------------------------#
    vendor_name           = property(lambda s: s.__data[0], lambda s,v: self.__data.__setitem__(0,v))
    product_code          = property(lambda s: s.__data[1], lambda s,v: self.__data.__setitem__(1,v))
    major_minor_revision  = property(lambda s: s.__data[2], lambda s,v: self.__data.__setitem__(2,v))
    vendor_url            = property(lambda s: s.__data[3], lambda s,v: self.__data.__setitem__(3,v))
    product_name          = property(lambda s: s.__data[4], lambda s,v: self.__data.__setitem__(4,v))
    model_name            = property(lambda s: s.__data[5], lambda s,v: self.__data.__setitem__(5,v))
    user_application_name = property(lambda s: s.__data[6], lambda s,v: self.__data.__setitem__(6,v))


#---------------------------------------------------------------------------#
# Counters Handler
#---------------------------------------------------------------------------#
class ModbusCountersHandler(object):
    '''
    This is a helper class to simplify the properties for the counters

    '''
    __data = dict([(i, 0x0000) for i in range(9)])
    __names   = [
        'BusMessage',
        'BusCommunicationError',
        'BusExceptionError',
        'SlaveMessage',
        'SlaveNoResponse',
        'SlaveNAK',
        'SlaveBusy',
        'BusCharacterOverrun'
        'Event '
    ]

    def __iter__(self):
        ''' Iterater over the device counters

        :returns: An iterator of the device counters
        '''
        return izip(self.__names, self.__data.itervalues())

    def update(self, input):
        ''' Update the values of this identity
        using another identify as the value

        :param input: The value to copy values from
        '''
        for k,v in input.iteritems():
            v += self.__getattribute__(k)
            self.__setattr__(k,v)

    def reset(self):
        ''' This clears all of the system counters
        '''
        self.__data = dict([(i, 0x0000) for i in range(9)])

    def summary(self):
        ''' Returns a summary of the counters current status

        :returns: A byte with each bit representing each counter
        '''
        count, result = 0x01, 0x00
        for i in self.__data.values():
            if i != 0x00: result |= count
            count <<= 1
        return result

    #---------------------------------------------------------------------------#
    # Properties
    #---------------------------------------------------------------------------#
    BusMessage            = property(lambda s: s.__data[0], lambda s,v: s.__data.__setitem__(0,v))
    BusCommunicationError = property(lambda s: s.__data[1], lambda s,v: s.__data.__setitem__(1,v))
    BusExceptionError     = property(lambda s: s.__data[2], lambda s,v: s.__data.__setitem__(2,v))
    SlaveMessage          = property(lambda s: s.__data[3], lambda s,v: s.__data.__setitem__(3,v))
    SlaveNoResponse       = property(lambda s: s.__data[4], lambda s,v: s.__data.__setitem__(4,v))
    SlaveNAK              = property(lambda s: s.__data[5], lambda s,v: s.__data.__setitem__(5,v))
    SlaveBusy             = property(lambda s: s.__data[6], lambda s,v: s.__data.__setitem__(6,v))
    BusCharacterOverrun   = property(lambda s: s.__data[7], lambda s,v: s.__data.__setitem__(7,v))
    Event                 = property(lambda s: s.__data[8], lambda s,v: s.__data.__setitem__(8,v))

#---------------------------------------------------------------------------#
# Main server controll block
#---------------------------------------------------------------------------#
class ModbusControlBlock(Singleton):
    '''
    This is a global singleotn that controls all system information

    All activity should be logged here and all diagnostic requests
    should come from here.
    '''

    __mode = 'ASCII'
    __diagnostic = [False] * 16
    __instance = None
    __listen_only = False
    __delimiter = '\r'
    __counters = ModbusCountersHandler()
    __identity = ModbusDeviceIdentification()
    __events   = []

    #---------------------------------------------------------------------------#
    # Magic
    #---------------------------------------------------------------------------#
    def __str__(self):
        ''' Build a representation of the control block

        :returns: A string representation of the control block
        '''
        return "ModbusControl"

    def __iter__(self):
        ''' Iterater over the device counters

        :returns: An iterator of the device counters
        '''
        return self.__counters.__iter__()

    #---------------------------------------------------------------------------#
    # Events
    #---------------------------------------------------------------------------#
    def addEvent(self, event):
        ''' Adds a new event to the event log

        :param event: A new event to add to the log
        '''
        self.__events.insert(0, event)
        self.__events = self.__events[0:64] # chomp to 64 entries
        self.Counter.Event += 1

    def getEvents(self):
        ''' Returns an encoded collection of the event log.

        :returns: The encoded events packet
        '''
        events = [event.encode() for event in self.__events]
        return ''.join(events)

    #---------------------------------------------------------------------------#
    # Other Properties
    #---------------------------------------------------------------------------#
    Identity = property(lambda s: s.__identity)
    Counter  = property(lambda s: s.__counters)
    Events   = property(lambda s: s.__events)

    def reset(self):
        ''' This clears all of the system counters and the
            diagnostic register
        '''
        self.__events = []
        self.__counters.reset()
        self.__diagnostic = [False] * 16

    #---------------------------------------------------------------------------#
    # Listen Properties
    #---------------------------------------------------------------------------#
    def _setListenOnly(self, value):
        ''' This toggles the listen only status

        :param value: The value to set the listen status to
        '''
        self.__listen_only = value is not None

    ListenOnly = property(lambda s: s.__listen_only, _setListenOnly)

    #---------------------------------------------------------------------------#
    # Mode Properties
    #---------------------------------------------------------------------------#
    def _setMode(self, mode):
        ''' This toggles the current serial mode

        :param mode: The data transfer method in (RTU, ASCII)
        '''
        if mode in ['ASCII', 'RTU']:
            self.__mode = mode

    Mode = property(lambda s: s.__mode, _setMode)

    #---------------------------------------------------------------------------#
    # Delimiter Properties
    #---------------------------------------------------------------------------#
    def _setDelimiter(self, char):
        ''' This changes the serial delimiter character

        :param char: The new serial delimiter character
        '''
        if isinstance(char, str):
            self.__delimiter = char
        elif isinstance(char, int):
            self.__delimiter = chr(char)

    Delimiter = property(lambda s: s.__delimiter, _setDelimiter)

    #---------------------------------------------------------------------------#
    # Diagnostic Properties
    #---------------------------------------------------------------------------#
    def setDiagnostic(self, mapping):
        ''' This sets the value in the diagnostic register

        :param mapping: Dictionary of key:value pairs to set
        '''
        for entry in mapping.iteritems():
            if entry[0] >= 0 and entry[0] < len(self.__diagnostic):
                self.__diagnostic[entry[0]] = (entry[1] != 0)

    def getDiagnostic(self, bit):
        ''' This gets the value in the diagnostic register

        :param bit: The bit to get
        :returns: The current value of the requested bit
        '''
        if bit >= 0 and bit < len(self.__diagnostic):
            return self.__diagnostic[bit]
        return None

    def getDiagnosticRegister(self):
        ''' This gets the entire diagnostic register

        :returns: The diagnostic register collection
        '''
        return self.__diagnostic

#---------------------------------------------------------------------------# 
# Exported Identifiers
#---------------------------------------------------------------------------# 
__all__ = [
        "ModbusAccessControl",
        "ModbusDeviceIdentification",
        "ModbusControlBlock"
]