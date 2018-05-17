To run this...

1) RPI with camera running
	capture.py
	- captures and sends pictures to remote server
2) Server running
	server.py
	- receives data, verifies client, invokes job manager
3) Server running
	REACT Site
	Express Site as REACT backend

* To configure
	python3 jobmanager.py new_job manifest.json
	- generates new job with configured settings from manifest