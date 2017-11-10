# coding=utf-8
# ------------------------------------------------------------------------------------------------------
# TDA596 Labs - Server Skeleton
# server/server.py
# Input: Node_ID total_number_of_ID
# Student Group:
# Student names: John Doe & John Doe
# ------------------------------------------------------------------------------------------------------
# We import various libraries
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler  # Socket specifically designed to handle HTTP requests
import sys  # Retrieve arguments
from urlparse import parse_qs  # Parse POST data
from httplib import HTTPConnection  # Create a HTTP connection, as a client (for POST requests to the other vessels)
from urllib import urlencode  # Encode POST content into the HTTP header
from codecs import open  # Open a file
from threading import Thread  # Thread Management

# ------------------------------------------------------------------------------------------------------

# Global variables for HTML templates
board_frontpage_footer_template = open("lab1/server/board_frontpage_footer_template.html").read()
board_frontpage_header_template = open("lab1/server/board_frontpage_header_template.html").read()
boardcontents_template = open("lab1/server/boardcontents_template.html").read()
entry_template = open("lab1/server/entry_template.html").read()

# ------------------------------------------------------------------------------------------------------
# Static variables definitions
PORT_NUMBER = 8080


# ------------------------------------------------------------------------------------------------------




# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
class BlackboardServer(HTTPServer):
	# ------------------------------------------------------------------------------------------------------
	def __init__(self, server_address, handler, node_id, vessel_list):
		# We call the super init
		HTTPServer.__init__(self, server_address, handler)
		# we create the dictionary of values
		self.store = {}
		# We keep a variable of the next id to insert
		self.current_key = -1
		# our own ID (IP is 10.1.0.ID)
		self.vessel_id = vessel_id
		# The list of other vessels
		self.vessels = vessel_list

	# ------------------------------------------------------------------------------------------------------
	# We add a value received to the store
	def add_value_to_store(self, value):
		# We add the value to the store
		self.current_key = len(self.store)+1
		self.store[self.current_key] = value

	# ------------------------------------------------------------------------------------------------------
	# We modify a value received in the store
	def modify_value_in_store(self, key, value):
		# we modify a value in the store if it exists
		#if self.store.has_key(key):
		#	self.store[key] = value
		if key in self.store:
			self.store[key] = value

	# ------------------------------------------------------------------------------------------------------
	# We delete a value received from the store
	def delete_value_in_store(self, key):
		# we delete a value in the store if it exists
		if key in self.store:
			del self.store[key]
			self.current_key -= 1

	# ------------------------------------------------------------------------------------------------------
	# Contact a specific vessel with a set of variables to transmit to it
	def contact_vessel(self, vessel_ip, path, action, key, value):
		# the Boolean variable we will return
		success = False
		# The variables must be encoded in the URL format, through urllib.urlencode
		post_content = urlencode({'action': action, 'key': key, 'value': value})
		# the HTTP header must contain the type of data we are transmitting, here URL encoded
		headers = {"Content-type": "application/x-www-form-urlencoded"}
		# We should try to catch errors when contacting the vessel
		try:
			# We contact vessel:PORT_NUMBER since we all use the same port
			# We can set a timeout, after which the connection fails if nothing happened
			connection = HTTPConnection("%s:%d" % (vessel, PORT_NUMBER), timeout=30)
			# We only use POST to send data (PUT and DELETE not supported)
			action_type = "POST"
			# We send the HTTP request
			connection.request(action_type, path, post_content, headers)
			# We retrieve the response
			response = connection.getresponse()
			# We want to check the status, the body should be empty
			status = response.status
			# If we receive a HTTP 200 - OK
			if status == 200:
				success = True
		# We catch every possible exceptions
		except Exception as e:
			print "Error while contacting %s" % vessel
			# printing the error given by Python
			print(e)

		# we return if we succeeded or not
		return success

	# ------------------------------------------------------------------------------------------------------
	# We send a received value to all the other vessels of the system
	def propagate_value_to_vessels(self, path, action, key, value):
		# We iterate through the vessel list
		for vessel in self.vessels:
			# We should not send it to our own IP, or we would create an infinite loop of updates
			if vessel != ("10.1.0.%s" % self.vessel_id):
				# A good practice would be to try again if the request failed
				# Here, we do it only once
				self.contact_vessel(vessel, path, action, key, value)


# ------------------------------------------------------------------------------------------------------







# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# This class implements the logic when a server receives a GET or POST request
# It can access to the server data through self.server.*
# i.e. the store is accessible through self.server.store
# Attributes of the server are SHARED accross all request hqndling/ threads!
class BlackboardRequestHandler(BaseHTTPRequestHandler):
	# ------------------------------------------------------------------------------------------------------
	# We fill the HTTP headers
	def set_HTTP_headers(self, status_code=200):
		# We set the response status code (200 if OK, something else otherwise)
		self.send_response(status_code)
		# We set the content type to HTML
		self.send_header("Content-type", "text/html")
		# No more important headers, we can close them
		self.end_headers()

	# ------------------------------------------------------------------------------------------------------
	# a POST request must be parsed through urlparse.parse_QS, since the content is URL encoded
	def parse_POST_request(self):
		post_data = ""
		# We need to parse the response, so we must know the length of the content
		length = int(self.headers['Content-Length'])
		# we can now parse the content using parse_qs
		post_data = parse_qs(self.rfile.read(length), keep_blank_values=1)
		# we return the data
		return post_data

	# ------------------------------------------------------------------------------------------------------
	# ------------------------------------------------------------------------------------------------------
	# Request handling - GET
	# ------------------------------------------------------------------------------------------------------
	# This function contains the logic executed when this server receives a GET request
	# This function is called AUTOMATICALLY upon reception and is executed as a thread!
	def do_GET(self):
		print("Receiving a GET on path %s" % self.path)
		# Here, we should check which path was requested and call the right logic based on it
		if self.path == "/board":
			#reload the board
			self.do_GET_Index() #temporary
		else:
			#reload everything
			self.do_GET_Index()

	# ------------------------------------------------------------------------------------------------------
	# GET logic - specific path
	# ------------------------------------------------------------------------------------------------------
	def do_GET_Index(self): #for when to whole page is reloaded
		# We set the response status code to 200 (OK)
		self.set_HTTP_headers(200)
		# In practice, go over the entries list,
		# produce the boardcontents part,
		# then construct the full page by combining all the parts ...
		page = board_frontpage_header_template + boardcontents_template + board_frontpage_footer_template
		self.wfile.write(page)

		# try:
		# 	f = open("server/html_snapshot")
		# 	self.wfile.write(f.read())
		# 	f.close()
		# 	return
        #
		# except IOError:
		# 	self.send_error(404, 'file not found')
	# ------------------------------------------------------------------------------------------------------
	# we might want some other functions
	# ------------------------------------------------------------------------------------------------------
	# ------------------------------------------------------------------------------------------------------
	# Request handling - POST
	# ------------------------------------------------------------------------------------------------------
	def do_POST(self):
		print("Receiving a POST on %s" % self.path)
		# Here, we should check which path was requested and call the right logic based on it
		# We should also parse the data received
		# and set the headers for the client
		post_data = self.parse_POST_request()
		# If we want to retransmit what we received to the other vessels

		#submit
		if self.path == "/board":
			self.server.add_value_to_store(post_data)
			#entry = open("server/entry_template.html").read()
			entry = entry_template
			entry = entry % ("entries/" + str(self.server.current_key), self.server.current_key, post_data['entry'])

			print "%s" %entry
			self.set_HTTP_headers(200)
			self.wfile.write(entry)

		retransmit = False  # Like this, we will just create infinite loops!
		if retransmit:
			# do_POST send the message only when the function finishes
			# We must then create threads if we want to do some heavy computation
			#
			# Random content
			thread = Thread(target=self.server.propagate_value_to_vessels, args=("action", "key", "value"))
			# We kill the process if we kill the server
			thread.daemon = True
			# We start the thread
			thread.start()
		# ------------------------------------------------------------------------------------------------------
		# POST Logic
		# ------------------------------------------------------------------------------------------------------
		# We might want some functions here as well


# ------------------------------------------------------------------------------------------------------





# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# Execute the code
if __name__ == '__main__':

	## read the templates from the corresponding html files
	# .....

	vessel_list = []
	vessel_id = 0
	# Checking the arguments
	if len(sys.argv) != 3:  # 2 args, the script and the vessel name
		print("Arguments: vessel_ID number_of_vessels")
	else:
		# We need to know the vessel IP
		vessel_id = int(sys.argv[1])
		# We need to write the other vessels IP, based on the knowledge of their number
		for i in range(1, int(sys.argv[2]) + 1):
			#vessel_list.append("10.1.0.%d" % i)  # We can add ourselves, we have a test in the propagation
			vessel_list.append("127.0.0.%d" % i) #change this back to 10... to test on mininet

	# We launch a server
	server = BlackboardServer(('', PORT_NUMBER), BlackboardRequestHandler, vessel_id, vessel_list)
	print("Starting the server on port %d" % PORT_NUMBER)

	try:
		server.serve_forever()
	except KeyboardInterrupt:
		server.server_close()
		print("Stopping Server")
# ------------------------------------------------------------------------------------------------------
