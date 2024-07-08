def migrate(cr, version):
    cr.execute(
        """
        UPDATE pos_order
        SET fried_state = 'finish'
        """
    )
    cr.execute(
        """
        UPDATE sale_order
        SET fried_state = 'finish'
        """
    )