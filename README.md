Web Services Facade
===================

Web Services Facade creates a web-based frontend to invoke SOAP web services
using simple GET requests, making it possible to test such services either
manually or using automatized scanners such as Burp Suite or sqlmap.

License
-------

Client SSL glue code is from nitwit, with no license provided.
The rest of the project is available under MIT license.

Dependencies
------------

 - Python 2.7 (tested on 2.7.3)
 - SUDS (Debian/Ubuntu package: `python-suds`)
 - Flask (Debian/Ubuntu package: `python-flask`)
