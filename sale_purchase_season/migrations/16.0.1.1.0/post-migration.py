def migrate(cr, version):
    cr.execute("UPDATE sale_season SET state='ready'")
