from . import models
from . import wizard


def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning

    odoo_version = '15.0'

    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != odoo_version:
        raise Warning(('Module support Odoo series %s found {}.'.format(server_serie)) % (odoo_version))
    return True
