#!/usr/bin/python
# written by James Hodgkinson
# this should handle subnets and build a structure which makes sense to people using Riverbed Cascade groupings
# only works with ipv4 for now

# requires bitstring
import sys 
import re
from bitstring import BitArray, BitStream, Bits
 
re_v4 = re.compile( "[\d]{1,3}.[\d]{1,3}.[\d]{1,3}.[\d]{1,3}" )
import logging

class Subnet( object ):
	def __init__( self, address, bits, description="", version=4 ):
		""" define a subnet 
		pass str( address ), int( bitsize ) and int( version )
		"""
		# only supports version 4 now
		self.description = description
		self.set_version( version )
		self.set_address( address )
		self.bits = bits
		self.children = []
		self.validate()

	def __repr__( self ):
		""" should return a CIDR representation of the subnet """
		return "{}/{}".format( self.address, self.bits )
	
	class SubnetException(Exception):
		pass	

	def bits2integer( self, bits ):
		""" converts the binary interpretation of the address into a dotted integer interpretation 
		currently only works with Bits() objects
		"""
		return "{}.{}.{}.{}".format( bits[:8].uint,  bits[8:16].uint, bits[16:24].uint, bits[24:32].uint )

	def binary_netmask( self, reset=False ):
		""" takes the current netmask and converts it to a binary mask """
		netmask_string = ( "1" * self.bits) + ( ( 32 - self.bits ) * "0" )
		self.netmask = BitArray( bin=netmask_string )
		return self.netmask

	def binary_wildcard( self, reset=False ):
		""" returns the binary interpretation of the wilcard mask """
		wildcard = self.binary_netmask().copy()
		wildcard.invert()
		self.wildcard = wildcard
		return wildcard

	def binary_address( self ):
		""" return a binary representation of the network address """
		a,b,c,d = self.address.split( "." )
		address = ( BitArray( uint=int( a ), length=8 ).bin + \
					BitArray( uint=int( b ), length=8 ).bin + \
					BitArray( uint=int( c ), length=8 ).bin + \
					BitArray( uint=int( d ), length=8 ).bin ) 
		return BitArray( bin=address )

	def binary_network_address( self ):
		""" returns the binary network address """
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
				
	def set_mask( self, newmask ):
		""" sets a new subnet mask, and adjusts the address to the network address to match the new mask. 
		examples
		192.168.0.152/32 => 192.168.0.0/24
		10.2.3.0/24 => 10.0.0.0/8
		1.2.3.0/24 => 1.2.3.0/32
		Tempted to throw an error when setting to a tighter mask, but hey... people do these things.
		"""
		if self.bits < newmask:
			logging.info( "New mask is tighter, be aware." )
		print( "Seting netmask to : {}".format( newmask ) )
		print( "Current address:    {}".format( self.binary_address() ) )
		self.bits = newmask
		print( "New binary netmask: {}".format( self.binary_netmask() ) )
		newaddress =  self.binary_address() & self.binary_netmask()
		print( "New binary address: {}".format( newaddress ) )

		print( "Hex: {}".format( newaddress.hex ) )
		string_address = []
		# iterate through the string in two-character chunks
		for i in range( 4 ):
			# slice to get hex, convert to string, then to an integer, then to a string. :)
			string_address.append( str( int( str( newaddress.hex )[(0+i*2):(2+i*2)], 16 ) ) ) 
		self.address = ".".join( string_address )
		print( "New address: {}".format( self.address ) )
		self.validate() # just to make sure
			
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
	
	def can_be_child( self, newnet, add=False ):
		""" give it a subnet object and test if it'll fit within 
			if add is True, automatically add to slot """
		
		if( newnet in self.children ): 	# if it already exists, return True - this doesn't work with
										# really complex subnets, just new ones
			return True
		if( newnet.bits <= self.bits ):	# if it's a larger space or the same thing, say no
			return False

		# before checking children, then test if the masks match
		masked_me = self.binary_netmask() & self.binary_address()
		masked_address = self.binary_netmask() & newnet.binary_address()
		if(  masked_address == masked_me ):
			if len( self.children ) > 0:	# check the children
				for child in self.children:
					if child.can_be_child( newnet, add ) == True:
						return True
				# if no matching children, then false
				return False	
			elif len( self.children ) == 0 and add == True:
				# add the thing
				self.children.append( newnet )
			return True
		# finally say no
		return False
	
	def print_tree( self, depth=0 ):
		retval = "+{}{}\n".format( depth*'-', self )
		if( len( self.children ) > 0 ):
			for child in self.children:
				retval += child.print_tree( depth+1 )
		return retval
						
if __name__ == '__main__':
	"""subnet = Subnet( "131.242.34.44", 32 )
	print( subnet.binary_wildcard() )
	print( subnet.binary_address() )
	print( subnet.binary_network_address() )
	print( subnet.binarydump() )
	print( subnet )
	subnet.set_mask( 24 )
	print( subnet )
	subnet.set_mask( 32 )
	print( subnet )
	print( subnet.get_bits() > 24 )"""
	x = Subnet( "0.0.0.0", 0 )
	print x.can_be_child( Subnet( "10.2.3.4", 32 ) )
	print x.can_be_child( Subnet( "11.2.3.4", 32 ) )