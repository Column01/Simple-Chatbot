

def test_list_item(list, index):
    try:
        test = list[index]
        return True
    except IndexError:
        return False