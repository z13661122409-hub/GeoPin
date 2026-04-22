# Security Notes

GeoPin is designed to be easy to audit and easy to trust.

## Default behavior

GeoPin does:

- geocode place names
- store tiny local sessions
- serve a local visualization page

GeoPin does not:

- read local files
- browse the filesystem
- access contacts, email, or passwords
- request device GPS permissions
- execute shell commands

## Network usage

By default GeoPin uses a geocoding service and loads globe viewer assets from the public web.

If you need stricter control, you can:

- swap the geocoder for an internal service
- vendor the front-end assets locally
- run GeoPin behind your own network policy
