from odoo.fields import Many2many


class Many2manyView(Many2many):
    """ This field have to be used when m2m relation is not standard
        and have to be created manualy. For example SQL Views.
    """
    def update_db(self, model, columns):
        # Do nothing. View have to be created elsewhere
        return True
