import sys

# This code exists for backwards compatibility reasons.
# I don't like it either. Just look the other way. :)

for package in ('odoo.addons.hubster_odoo_integration.python_library.urllib3', 'odoo.addons.hubster_odoo_integration.python_library.idna', 'odoo.addons.hubster_odoo_integration.python_library.chardet'):
    locals()[package] = __import__(package)
    # This traversal is apparently necessary such that the identities are
    # preserved (requests.packages.urllib3.* is urllib3.*)
    for mod in list(sys.modules):
        if mod == package or mod.startswith(package + '.'):
            sys.modules['requests.packages.' + mod] = sys.modules[mod]

# Kinda cool, though, right?
