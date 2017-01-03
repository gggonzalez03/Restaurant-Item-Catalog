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
                output += "<br><br><br><a href='/restaurant/new'>Add a new restaurant</a></body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurant/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurant'>'''
                output += '''<h2>What's the new name of your restaurant</h2><input name="message" type="text" >'''
                output += '''<input type="submit" value="Submit"></form>'''
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/restaurant/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurant/new'>'''
                output += '''<h2>What's the new name of your restaurant</h2><input type="hidden" name="purpose" value="new">'''
                output += '''<input name="newrestaurantname" type="text" >'''
                output += '''<input type="submit" value="Submit"></form>'''
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
                messagecontent = fields.get('purpose')
                if len(messagecontent) == 1:
                    if messagecontent[0] == "new" and isinstance(messagecontent[0], str):
                        new_restaurant_name = fields.get("newrestaurantname")
                        restaurant_queries.add_restaurant(new_restaurant_name[0])
                        self.wfile.write(new_restaurant_name)
                print messagecontent[0], type(messagecontent[0])
        except:
            pass

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
