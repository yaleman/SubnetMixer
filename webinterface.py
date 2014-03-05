#!/usr/bin/python

from subnet import Subnet

from flask import Flask


app = Flask(__name__)

@app.route( "/" )
def index():
	retval = "<pre>"
	for (n,b) in [ ("123.234.99.21", 8), ("123.234.99.21", 24), ("192.168.0.2", 25), ("10.2.3.4", 32 ) ]:
		subnet = Subnet( n, b )

		retval +=  "#" * 50 + "\n"
		retval += str( subnet )+"\n"
		try:
			retval += str( subnet.validate() )+"\n"
		except subnet.SubnetException, e:
			retval += "{}\n".format( str( e ) )
		#retval += "\ntesting ipv4toint\n"
		#retval += "{}\n".format( str( subnet.ipv4toint( subnet.address ) ) )
		retval += "dumping binary\n"
		retval += "{}\n".format( str(  subnet.binarydump() ) ) 

	return retval


if __name__ == "__main__":
	app.run( debug=True )

	#("0.0.0.0", 0 ), 