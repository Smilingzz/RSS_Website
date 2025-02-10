# Webserver

- It accepts requests/communication from Gunicorn which is a
Web Server Gateway Interface. 
- NGINX serves as a reverse-proxy, i.e. serving client requests and 
forwarding them to the webserver.

## Topology

SQLite <-> Flask <-> Gunicorn <-> NGINX <-> DNS <-> Client

## Architecture requirements/dependencies

1.  The server requires a certificate, which is to be signed.
    This is best done using certbot through NGINX.
2.  Something to serve the DNS requests which will resolve the domain
    to the public IP address of the server.
    An easy solution is to find out your public IP and then register for 
    Cloudflare to provide a DNS resolver. A domain must also be purchased.
3.  Port-forwarding must be setup on the device (usually router) which serves the DNS redirects.

Essentially, the certificate exists to allow for a secure connection (HTTP over TLS),
the DNS enables clients to resolve a domain (e.g. svt.se) to a public IP address and port.
The port-forwarding enables the externally facing device (router) to know which internal IP address
(e.g. 192.168.0.277) and port (e.g. DNS sends to ROUTER_=_PUBLIC_IP_AND_PORT_=_52333 and the router from
there knows and requests to port 52333 should be forwarded to 192.168.0.227 and port 443).