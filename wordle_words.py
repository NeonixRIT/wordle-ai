import ast

ASSETS_PATH = '/assets'
POSSIBLE_ANSWERS_PATH = f'.{ASSETS_PATH}/wordle-answers.txt'
WORDS = sorted([word.strip() for word in open(POSSIBLE_ANSWERS_PATH).readlines()]) # Possible answers
CONDITIONS_PATH = f'.{ASSETS_PATH}/conditions.json'

with open(CONDITIONS_PATH) as f:
    data = f.read()
CONDITIONS = ast.literal_eval(data)

print(CONDITIONS)

# Remove any words that don't include the letters we know are good
NEW_WORDS = list()
for word in WORDS:
    keep = True
    for mustContain in CONDITIONS['Included']:
        if mustContain not in word:
            keep = False
    if keep:
        NEW_WORDS.append(word)
WORDS = NEW_WORDS

# Remove any words that include letters we know are not good
NEW_WORDS = list()
for word in WORDS:
    keep = True
    for mustExclude in CONDITIONS['Excluded']:
        if mustExclude in word:
            keep = False
    if keep:
        NEW_WORDS.append(word)
WORDS = NEW_WORDS

# Remove any words that don't have the good letters in the correct positions
for pos in '12345':
    NEW_WORDS = list()
    for word in WORDS:
        mustMatch = CONDITIONS[pos]
        if mustMatch == '' or word[int(pos)-1] == mustMatch:
            NEW_WORDS.append(word)
    WORDS = NEW_WORDS

# Remove any words that have the good letters in the wrong positions
i = -1
for pos in 'abcde':
    i += 1
    NEW_WORDS = list()
    for word in WORDS:
        mustExclude = CONDITIONS[pos]
        if len(mustExclude) == 0:
            NEW_WORDS.append(word)
        else:
            for keepOut in mustExclude:
                if word[int(i)] != keepOut:
                    if word not in NEW_WORDS:
                        NEW_WORDS.append(word)
    WORDS = NEW_WORDS

print(WORDS)
print(len(WORDS))

