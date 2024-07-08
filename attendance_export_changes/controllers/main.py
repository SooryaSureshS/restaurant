from odoo import http
from odoo.http import request
import io
import logging
from odoo.tools.translate import _
from odoo.addons.web.controllers.main import ExportXlsxWriter
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.tools import image_process, topological_sort, html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, float_repr
import datetime
from odoo.http import JsonRequest, AuthenticationError, SessionExpiredException, ustr, serialize_exception
import odoo.exceptions

_logger = logging.getLogger(__name__)


def __init__(self, field_names, row_count=0):
    self.field_names = field_names
    self.output = io.BytesIO()
    self.workbook = xlsxwriter.Workbook(self.output, {'in_memory': True})
    self.base_style = self.workbook.add_format({'text_wrap': True})
    self.header_style = self.workbook.add_format({'bold': True})
    self.header_bold_style = self.workbook.add_format({'text_wrap': True, 'bold': True, 'bg_color': '#e9ecef'})
    self.date_style = self.workbook.add_format({'text_wrap': True, 'num_format': 'yyyy-mm-dd'})
    self.datetime_style = self.workbook.add_format({'text_wrap': True, 'num_format': 'yyyy-mm-dd hh:mm:ss'})
    self.float_style = self.workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00'})
    self.worksheet = self.workbook.add_worksheet()
    self.value = False

    if row_count > self.worksheet.xls_rowmax:
        raise UserError(
            _('There are too many rows (%s rows, limit: %s) to export as Excel 2007-2013 (.xlsx) format. Consider splitting the export.') % (
            row_count, self.worksheet.xls_rowmax))


setattr(ExportXlsxWriter, '__init__', __init__)


def write_cell(self, row, column, cell_value):
    cell_style = self.base_style

    if isinstance(cell_value, bytes):
        try:
            # because xlsx uses raw export, we can get a bytes object
            # here. xlsxwriter does not support bytes values in Python 3 ->
            # assume this is base64 and decode to a string, if this
            # fails note that you can't export
            cell_value = pycompat.to_text(cell_value)
        except UnicodeDecodeError:
            raise UserError(
                _("Binary fields can not be exported to Excel unless their content is base64-encoded. That does not seem to be the case for %s.",
                  self.field_names)[column])

    if isinstance(cell_value, str):
        if len(cell_value) > self.worksheet.xls_strmax:
            cell_value = _(
                "The content of this cell is too long for an XLSX file (more than %s characters). Please use the CSV format for this export.",
                self.worksheet.xls_strmax)
        else:
            cell_value = cell_value.replace("\r", " ")
    elif isinstance(cell_value, datetime.datetime):
        cell_style = self.datetime_style
    elif isinstance(cell_value, datetime.date):
        cell_style = self.date_style
    elif isinstance(cell_value, float):
        cell_style = self.float_style
    elif isinstance(cell_value, (list, tuple)):
        cell_value = pycompat.to_text(cell_value)
    self.write(row, column, cell_value, cell_style)

setattr(ExportXlsxWriter, 'write_cell', write_cell)