try:
    from SqliteSearch import SqliteReadDB
except ImportError:
    import SqliteReadDB


def response_format(e, settings, cmd):
    username = e.tags[3]['value']
    user_id = e.tags[12]['value']
    currency = SqliteReadDB.read_currency(user_id)
    for i in settings['commands']:
        if i == cmd:
            response = settings['commands'][cmd]['response'].format(username=username, currency=currency, command=cmd)
            return response
        else:
            pass
    else:
        response = "Unknown command '{}'. Did you type it correctly?".format(cmd)
    return response
