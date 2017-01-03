from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import re
import os
import cgi
import restaurant_queries
import subprocess


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurant"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = "<!DOCTYPE html><html><head><title>Restaurants</title></head><body>"
                for restaurant in restaurant_queries.get_all_restaurants():
                    output += "<h2>%s</h2><a href='/restaurant/id/edit'>Edit</a><br><a href='/restaurant/delete'>Delete</a>" % (restaurant.name)
                self.wfile.write(output)
                output += "<a href='/restaurant/new'>Add a new restaurant</a></body></html>"
                print output
                return

            if self.path.endswith("/restaurant/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>Are you sure you want to delete?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
            output = ""
            output += "<html><body>"
            output += " <h2> Okay, how about this: </h2>"
            output += "<h1> %s </h1>" % messagecontent[0]
            output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
            output += "</body></html>"
            self.wfile.write(output)
            print output
        except:

def get_pids(port):
    command = "lsof -i :%s | awk '{print $2}'" % port
    pids = subprocess.check_output(command, shell=True)
    pids = pids.strip()
    if pids:
        pids = re.sub(' +', ' ', pids)
        for pid in pids.split('\n'):
            try:
                yield int(pid)
            except:
                pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()
        # kill the processes in port 8080
        # including this python script
        port = 8080
        pids = set(get_pids(port))
        command = 'kill -9 {}'.format(' '.join([str(pid) for pid in pids]))
        os.system(command)

if __name__ == '__main__':
    main()
