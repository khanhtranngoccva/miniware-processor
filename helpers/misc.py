def is_valid_ip(ip: str):
    tok = ip.split(".")
    if len(tok) != 4:
        return False
    for str_val in tok:
        try:
            int_val = int(str_val)
            if not 0 <= int_val <= 255:
                return False
        except ValueError:
            return False
    return True
