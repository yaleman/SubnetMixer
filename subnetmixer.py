#!/usr/bin/python
# written by James Hodgkinson
# this should handle subnets and build a structure which makes sense to people using Riverbed Cascade groupings
# only works with ipv4 for now
import sys 
import re


 
re_v4 = re.compile( "[\d]{1,3}.[\d]{1,3}.[\d]{1,3}.[\d]{1,3}" )
 
class Subnet():
	def __init__( self, address, bits, version=4 ):
		""" define a subnet 
		pass str( address ), int( bitsize ) and int( version )
		"""
		# only supports version 4 now
		if( version != 4 ):
			self.throwv4error()
		else:
			self.version = version
		
		self.set_address( address )
		self.bits = bits
		self.children = {}


	def __repr__( self ):
		""" should return a CIDR representation of the subnet """
		return "{}/{}".format( self.address, self.bits )
	
	class SubnetException(Exception):
		
		pass	


	def raiseerror( self, message ):
		""" raises an error based on this class """
		raise self.SubnetException( { 'message' : message } )

	def set_address( self, address ):
		""" sets the address field, also requests recalculation of the integer values of the field 
		pass str( address )
		"""
		if self.version == 4:
			if( re_v4.match( address ) == None ):
				self.raiseerror( "Address is set as version 4 but incorrectly defined: {}".format( address ) )
		self.address = address
			
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
				
for (n,b) in [ ("192.168.0.2", 2), ("0.0.0.0", 0 ), ("10.2.3.4", 33 ) ]:
	print "#" * 50
	print n, b
	subnet = Subnet( n, b )
	try:
		print subnet.validate()
	except subnet.SubnetException, e:
		print e
	print subnet