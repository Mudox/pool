import random
import operator
import collections
import math

def picker(weight=0.75):

    """
    weight: the larger the weight, the chances higher elements got picked up.
            if weight < 0.5, the lower elements got more chances to be picked up
            than higher elements.
    """

    def weighted_pick(items):
        """
        items: ordered sequence.

        this function pick from the sequence a element & return it.

        it trys its best to make the elements at higher index get more chances to
        be picked up.
        """

        balls = items

        while len(balls) != 1:
            mid_index = len(balls) / 2
            dice = random.random()
            if dice > weight:
                balls = balls[:mid_index]
            else:
                balls = balls[mid_index:]

        return balls[0]

    return weighted_pick

items = []
for n in range(26):
    name = chr(0x41 + n)
    i = random.randrange(16)
    items.append((name, i))

if __name__ == '__main__':
    print('before sorting: {}'.format(items))
    items.sort(key=operator.itemgetter(1))
    print('after sorting: {}'.format(items))

    p = picker()

    stats = collections.defaultdict(int)
    for _ in range(100000):
        picked = p(items)
        stats[picked] += 1

    ret = []
    for t, n in stats.items():
        ret.append((n, t))

    ret.sort(key=operator.itemgetter(0))
    for x in ret:
        print(x)
