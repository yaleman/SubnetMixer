#!/usr/bin/python

from subnet import Subnet

from flask import Flask


app = Flask(__name__)

@app.route( "/" )
def index():
	subnets = []
	retval = "<pre>"
	for (n,b, desc) in [ 
		( '0.0.0.0', 0, 'root' ), 
		("123.234.99.21", 8, 'test 1'), 
		("123.234.99.21", 24, 'test 2'), 
		("192.168.0.2", 24, 'test 3'), 
		("192.168.0.2", 25, 'test 3'), 
		("10.2.3.4", 32, 'test 4' ), ]:
		newnet = Subnet( n, b, desc )
		retval += "{}\n{}\n".format( "#"*50, newnet )
		waschild = False
		if len( subnets ) == 0:
			retval += "Added this as the root\n"
			subnets.append( newnet )
			waschild = True
		else:
			for net in subnets:
				retval += "Checking if {} is a child of {}\n".format( newnet, net )
				if net.can_be_child( newnet ) == True:
					subnets[subnets.index( net )].children.append( newnet )
					retval += "Woo, found a slot! Child of {}\n".format( net )
					waschild = True
					retval += "{}\n".format( subnets )
			if waschild == False:		
				retval += "Added another root\n"	
				subnets.append( newnet )
		retval+= "{}\n".format( subnets )	

		#try:
		#	retval += str( subnet.validate() )+"\n"
		#except subnet.SubnetException, e:
		#	retval += "{}\n".format( str( e ) )
		#retval += "\ntesting ipv4toint\n"
		#retval += "{}\n".format( str( subnet.ipv4toint( subnet.address ) ) )
		#retval += "dumping binary\n"
		#retval += "{}\n".format( str(  newnet.binarydump() ) ) 

	retval += "{}\n".format( subnets )
	for s in subnets:
		retval += s.print_tree()+"\n"
	return retval


if __name__ == "__main__":
	app.run( debug=True )

	#("0.0.0.0", 0 ), 