def set_effective_dates(cr):
    cr.execute(
        """
        UPDATE nh_activity SET effective_date_terminated = date_terminated WHERE effective_date_terminated IS NULL
        """
    )


def migrate(cr, version):
    if not version:
        return
    set_effective_dates(cr)
