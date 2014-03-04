import re
re_v4 = re.compile( "[\d]{1,3}.[\d]{1,3}.[\d]{1,3}.[\d]{1,3}" )

tests = [ "10.0.0.0", "10.0.0", "1111" ]

for x in tests:
    print re_v4.match( x )
