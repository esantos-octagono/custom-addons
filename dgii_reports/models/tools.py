# -*- coding: utf-8 -*-

def is_ncf(value, type):
    if not value:
        return False

    value = value.strip()
    if len(value) == 11:
        try:
            if type in ("in_refund","out_refund") and value[0] == 'B' and value[1:3] == '04' and int(value[3:11]):
                return True
            elif type == "in_invoice" and value[0] == 'B' and value[1:3] in ('01','14','15','11','13') and int(value[3:11]):
                return True
            elif type == "out_invoice" and value[0] == 'B' and value[1:3] in ('01','02','14','15','11','13') and int(value[3:11]):
                return True
        except:
            pass
    return False