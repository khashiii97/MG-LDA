from emoji import UNICODE_EMOJI
import operator
emojis_list = list(UNICODE_EMOJI.keys())
emojis_list.append('😂')
emojis_list.append('⚖')
emojis_list.append('😊')
emojis_list.append('|-')
emojis_list.append('👇')
emojis_list.append('🤔')
emojis_list.append('💙')
emojis_list.append('👍')
emojis_list.append('😐')
emojis_list.append('😥')
emojis_list.append('!')
emojis_list.append('?')
emojis_list.append('؟')
emojis_list.append('=')
emojis_list.append('/')
emojis_list.append('+')
emojis_list.append('*')


def remove_emoji(s):# the helps us dispense emojis in verbs
    count = 0
    for emoji in emojis_list:
        if emoji in s:
            s = s.replace(emoji,'')
    return s
slang_verbs = {} # dictionary from verb to frequency
with open('../SLangs/lscp-0.5-fa-derivation-tree.txt', 'r', encoding='utf-8') as in_file:
    head = [next(in_file) for x in range(50000)]
    # strings = in_file.read().split("\n")
    for h in head:
        list_h = eval(h)
        for p,POS_tuple in enumerate(list_h):
            if 'V' in POS_tuple and len(POS_tuple) == 2:
                if '\u200c' in POS_tuple[0]:
                    list_h[p] = (list_h[p][0].replace('\u200c',''),'V')
                if '-' in POS_tuple[0]:
                    list_h[p] = (list_h[p][0].replace('-',' '),'V')
                if '_' in POS_tuple[0]:
                    list_h[p] = (list_h[p][0].replace('_',' '),'V')
                list_h[p] = (remove_emoji(list_h[p][0]), 'V')
                if list_h[p][0] in slang_verbs:
                    slang_verbs[list_h[p][0]] += 1
                else:
                    slang_verbs[list_h[p][0]] = 1

sorted_slang_verbs = sorted(slang_verbs.items(), key=operator.itemgetter(1))
print('\u200c' in 'می\u200cکنید')
with open('slang_verbs.txt', 'w', encoding='utf-8') as in_file:
    for s in sorted_slang_verbs:
        in_file.write(str(s[0]) + '\n')

