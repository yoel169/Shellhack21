#unicode emojies
emojies = {

'wizard' : '\U0001F9D9','!': '\U00002757', 'shell': '\U0001F41A', 'check': '\U00002705', 'smile': '\U0001F604', 
'sweat': '\U0001F605', 'cry': '\U0001F622', 'monkey': '\U0001F648', 'car': '\U0001F697', 'race car': '\U0001F6FB',
'wrench': '\U0001F527', 'book': '\U0001F4D6', 'calandar': '\U0001F5D3', 'mechanic': '\U0001F9D1' + '\U0000200D' + 
'\U0001F527', 'phone': '\U0001F4DE', 'fax': '\U0001F4E0', 'penguin': '\U0001F427', 'card': '\U0001F4C7', 
'globe': '\U0001F310', 'watch': '\U0000231A', 'cross': '\U0000274C', 'collision': '\U0001F4A5', 'cash': '\U0001F4B5'

}

def getEmojie(name):
    if name in emojies:
        return emojies[name]
    else:
        return None