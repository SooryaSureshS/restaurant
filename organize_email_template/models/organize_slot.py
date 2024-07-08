import pytz
from future.backports.datetime import timedelta

from odoo import api, fields, models, _


class StudentCard(models.AbstractModel):
    _name = 'report.organize_email_template.organize_report_template'

    @api.model
    def _get_report_values(self, docids, data):
        destination_tz = pytz.timezone(self.env.user.tz or 'Australia/Brisbane')

        # destination_tz = pytz.timezone('Asia/Kolkata')
        docs = self.env['organize.slot'].browse(docids)
        start = data['start_date']
        end = data['end_date']
        dict_date = {}
        dates_list_other = []
        satrt_end_dates = {"start_date": str(start.strftime("%d")) + " " + str(start.strftime("%B")) + " " + str(
            start.year) + "-" + str(end.strftime("%d")) + " " + str(end.strftime("%B")) + " " + str(end.year)}
        dates_list = self.get_date_list(start, end)
        dates_list_year = self.get_date_list_other(start, end)
        dates_list_other = self.get_date_list_other(start, end)
        organize_search = self.env['organize.slot'].sudo().search([])
        for rec in organize_search:
            date_list = []
            common = []
            common_new = []
            res_dct = {}
            # start_t = rec.start_datetime
            # end_t = rec.end_datetime
            start_tt = pytz.utc.localize(rec.start_datetime).astimezone(
                destination_tz).replace(tzinfo=None)
            end_tt = pytz.utc.localize(rec.end_datetime).astimezone(
                destination_tz).replace(tzinfo=None)
            date_list = (self.get_date_list_other(start_tt, end_tt))
            common = list(set(dates_list_other).intersection(date_list))
            if len(common) != 0:
                c = sorted(common, key=dates_list_year.index)
                if dates_list_year[0] not in c:
                    c.insert(0, "0")
                if dates_list_year[1] not in c:
                    c.insert(0 + 1, "0")
                if dates_list_year[2] not in c:
                    c.insert(0 + 2, "0")
                if dates_list_year[3] not in c:
                    c.insert(0 + 3, "0")
                if dates_list_year[4] not in c:
                    c.insert(0 + 4, "0")
                if dates_list_year[5] not in c:
                    c.insert(0 + 5, "0")
                if dates_list_year[6] not in c:
                    c.insert(0 + 6, "0")
                if rec.role_id.name:
                    role = str(rec.role_id.name)
                else:
                    role = " "
                for val in c:
                    if val != "0":
                        index = c.index(val)
                        s_date = pytz.utc.localize(rec.start_datetime).astimezone(
                            destination_tz).replace(tzinfo=None)
                        e_date = pytz.utc.localize(rec.end_datetime).astimezone(
                            destination_tz).replace(tzinfo=None)
                        c[index] = str(
                            s_date.strftime("%I")) + ": " + str(
                            s_date.strftime("%M")) + " " + str(
                            s_date.strftime("%p")) + " - " + str(
                            e_date.strftime("%I")) + ": " + str(
                            e_date.strftime("%M")) + " " + str(
                            e_date.strftime("%p")) + "(" + str(role) + ")"
                c.insert(0 + 7, rec.employee_id.name)
                c.insert(0 + 8, rec.role_id.name)

                role_dates = str(rec.start_datetime.strftime("%d")) + "" + str(
                    rec.start_datetime.strftime("%b")) + "," + "" + str(
                    rec.start_datetime.strftime("%I")) + "" + str(
                    rec.start_datetime.strftime("%p")) + "--" + role + "--" + str(
                    rec.end_datetime.strftime("%d")) + "" + str(
                    rec.end_datetime.strftime("%b")) + "" + str(
                    rec.start_datetime.strftime("%I")) + "" + str(
                    rec.start_datetime.strftime("%p"))
                c.insert(0 + 9, role_dates)
                c.insert(0 + 10, role)
                if rec.employee_id.id in dict_date.keys():
                    dict_date[rec.employee_id.id].append(dict(zip(range(len(c)), c)))
                else:
                    dict_date[rec.employee_id.id] = [dict(zip(range(len(c)), c))]
        return {
            'doc_ids': docids,
            'doc_model': 'organize.slot',
            'docs': docs,
            'dates': satrt_end_dates,
            'dates_list': dates_list,
            'dict_date': dict_date,

        }

    def get_date_list(self, date1, date2):
        date_list = []
        date_list_1 = []
        start = date1
        end = date2
        delta = end - start
        for i in range(delta.days + 1):
            date_list_1.append(start + timedelta(days=i))
        for rec in date_list_1:
            word_date = str(rec.strftime("%A")) + " " + str(rec.strftime("%b")) + "" + str(rec.strftime("%d"))
            date_list.append(word_date)

        return date_list

    def get_date_list_other(self, date1, date2):
        date_list = []
        date_list_1 = []
        start = date1
        end = date2
        delta = end - start
        # print(start,end,"inside function")
        for i in range(delta.days + 1):
            date_list_1.append(start + timedelta(days=i))
        for rec in date_list_1:
            word_date = str(rec.strftime("%A")) + " " + str(rec.strftime("%b")) + "" + str(
                rec.strftime("%d")) + " " + str(rec.strftime("%Y"))
            date_list.append(word_date)

        return date_list
