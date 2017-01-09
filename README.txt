1. Install VirtualBox if you dont have it in your system:
	https://www.virtualbox.org
2. Install Vagrant
	https://www.vagrantup.com
3. Create a Google credential
	a. Go to https://console.developers.google.com and login of necessary
	b. Create a new project and it will redirect the page to the dashboard
	c. On the left hand side, click on Credentials
	d. Select the dropdown for "Create credentials" and select "OAuth Client ID"
	e. When a new page loads, select Web Application as Application type
	f. Under Authorized Javascript  origins, include http://localhost:5000
	g. Under Authorized Redirect URIs, enter http://localhost:5000/restaurants
	h. Click Create
	i. For the OAuth screen you will have to provide your email and the name for 
		the project, which could be anything, and hit save.
	j. On your credentials page, click the one you just created and click
		"Download JSON"
	k. Rename the downloaded file to "client_secrets" and move it into the 
		repository
	l. After you have done all this, you will have your client_id in your client_secrets
		json file.
	m.Look for the client_id in the client_secrets json file and copy it
	n. Open login.html and search through the file for "YOUR_CLIENT_ID_IN_HERE" and paste
		your client_id in place of the placeholder in quotations
4. Navigate to this repository in your local machine and run GitBash in 
	there. Alternatively, open GitBash anywhere and cd to this repository
5. Enter 'vagrant up'
	-this will initialize VirtualBox via Vagrant
6. Enter 'vagrant ssh'
	-this will log you in to the virtual machine that has been initialized
7. Enter cd /vagrant
	-Note that there is a '/' character before 'vagrant'
8. Run main_project.py by entering 'python main_project.py'