#!/usr/bin/python
# written by James Hodgkinson
# this should handle subnets and build a structure which makes sense to people using Riverbed Cascade groupings
# only works with ipv4 for now
import sys 
import re
from bitstring import BitArray, BitStream, Bits
 
re_v4 = re.compile( "[\d]{1,3}.[\d]{1,3}.[\d]{1,3}.[\d]{1,3}" )
 
class Subnet( object ):
	def __init__( self, address, bits, version=4 ):
		""" define a subnet 
		pass str( address ), int( bitsize ) and int( version )
		"""
		# only supports version 4 now
		self.set_version( version )
		self.set_address( address )
		self.bits = bits
		self.children = {}

	def __repr__( self ):
		""" should return a CIDR representation of the subnet """
		return "{}/{}".format( self.address, self.bits )
	
	class SubnetException(Exception):
		pass	

	def bits2integer( self, bits ):
		return "{}.{}.{}.{}".format( bits[:8].uint,  bits[8:16].uint, bits[16:24].uint, bits[24:32].uint )

	def binary_netmask( self, reset=False ):
		netmask_string = ( "1" * self.bits) + ( ( 32 - self.bits ) * "0" )
		self.netmask = BitArray( bin=netmask_string )
		self.flags['netmask'] = True
		return self.netmask
	def binary_wildcard( self, reset=False ):
		wildcard = self.binary_netmask().copy()
		wildcard.invert()
		self.wildcard = wildcard
		return wildcard
	def binary_address( self ):
		a,b,c,d = self.address.split( "." )
		address = (BitArray( uint=int( a ), length=8 ).bin + BitArray( uint=int( b ), length=8 ).bin + 
			BitArray( uint=int( c ), length=8 ).bin + BitArray( uint=int( d ), length=8 ).bin) 
		return BitArray( bin=address )

	def binary_network_address( self ):
		return self.binary_address() & self.binary_netmask()

	def binarydump( self ):
		""" takes the currently defined subnet and dumps a bunch of binary data, will be handy for later things. """
		# handy ref http://www.aboutmyip.com/AboutMyXApp/SubnetCalculator.jsp?ipAddress=10.2.3.4&cidr=32
		retval = ""		
		

		
		retval = "Address: \t{}\n".format( self.binary_address().bin )		
		retval += "Netaddrs: \t{}\n".format( self.binary_network_address().bin )
		retval += "Netmask: \t{}\n".format( self.binary_netmask().bin )
		retval += "Wildcard: \t{}\n".format( self.binary_wildcard().bin )
		retval += "Netmask: \t{}\n".format( self.bits2integer( self.binary_netmask() ) )

		return retval

	def ipv4toint( self, address ):
		""" takes an ip address in string form and turns it to an integer 
		pass str( address )
		returns false if it's an invalid string
		"""
		# test ipv4toint( "192.168.0.2" ) == 3232235522
		# test ipv4toint( "0.0.0.0" ) == 0
		# test ipv4toint( "10.2.3.4" ) == 167904004
		if re_v4.match( address ) != None :
			# valid address
			a,b,c,d = address.split( "." )
			intval = ( int( a ) * ( 256 ** 3 ) ) + ( int( b ) * ( 256 ** 2 ) ) + ( int( c ) * 256 ) + int( d )
			return intval
		else:
			return False

	def raiseerror( self, message ):
		""" raises an error based on this class """
		#raise self.SubnetException( { 'message' : "Exception: "+message } )
		raise self.SubnetException( "Exception: {}".format( message ) )

	def set_version( self, version ):
		""" sets the version number, checks if it's 4 - for now only IPV4 is supported.
		>>> subnet.set_version( 4 )
		True
		>>> subnet.set_version( 6 )
		False
		"""
		if( version != 4 ):
			self.throwv4error()
			return False
		else:
			self.version = version
			return True
			
	def set_address( self, address ):
		""" sets the address field, also requests recalculation of the integer values of the field 
		pass str( address )
		"""
		if self.version == 4:
			if( re_v4.match( address ) == None ):
				self.raiseerror( "Address is set as version 4 but incorrectly defined: {}".format( address ) )
				return False
			else:
				self.address = address
				return True
			
	def throwv4error( self ):
		""" throws an error if you're using something other than IPV4 while I'm still developing """
		self.raiseerror(  "Subnet {}/{} requested with version {}, only IPV4 supported for now".format( self.address, self.bits, self.version ) )
	
	def validate( self, checkchildren=False ):
		""" run a self check on the subnet as defined 
		pass bool( checkchildren )
		use checkchildren with care with large networks
		"""
		# self-test if the Subnet is defined properly
		# check if the bitsize is an integer
		if( sys.version_info < ( 3, 0 ) ):
			# running python 2
			if( isinstance( self.bits, ( int, long ) ) != True ):
				self.raiseerror( "Subnet {}/{} failed validation - bits isn't integer".format( self.address, self.bits ) )
		else:
			# running python 3.x
			if( isinstance( self.bits, int ) != True ):
				self.raiseerror(  "Subnet {}/{} failed validation - bits isn't integer".format( self.address, self.bits ) )

		# check if the bitsize is between 0 and 32
		if( self.version != 4 ):
			self.throwv4error()
		elif self.bits < 0 or self.bits > 32:
			self.raiseerror( "Subnet {}/{} bitsize out of range".format( self.address, self.bits ) )
		# if checkchildren is true, self-validate all child addresses.
		if( checkchildren ):
			for child in children:
				child.validate( True )
		return True
				


