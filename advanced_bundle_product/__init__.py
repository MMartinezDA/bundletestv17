# -*- coding: utf-8 -*-
from . import controllers
from . import models
from . import wizard
def pre_init_check(cr):
    from odoo.release import series
    from odoo.exceptions import ValidationError
    if series != '17.0':
        raise ValidationError(
            'Module support Odoo series 17.0 found {}.'.format(series))
