import math
from pprint import pprint
import random
import scipy.spatial.distance

pred = [.7,.1,.1,.1]
true = [.5,.2,.2,.1]

def calc_prob(history_list):
    prob = [0,0,0,0]
    for item in history_list:
        prob[item] += 1
    for i in range(len(prob)):
        prob[i] = round(prob[i]/len(history_list), 3)
    return prob


def model_distance(accept, test):
    return scipy.spatial.distance.cosine(accept, test)


def emulate_room(room):
    pass


def calc_trajectory(history):
    hypothesis = []
    hypothesis_dist = []
    hypothesis_split = []
    max_range = 10
    for i in range(max_range):
        half_length = math.floor(len(history)/2)
        variance = (len(history) / 5)

        # split_point = half_length + random.randint(-variance, variance)
        split_point = half_length + math.floor((variance / max_range) * (i - math.ceil(max_range/2)))

        new = history[split_point:]
        old = history[:split_point]

        # given a random split between the old and the new, figure out where the new should be?

        # calculate probability of new. thats a hypothesis.
        hypothesis.append(calc_prob(new))
        hypothesis_split.append(split_point)
        hypothesis_dist.append(round(model_distance(true, calc_prob(new)), 3))

    for i in range(len(hypothesis)):
        print(hypothesis_split[i], ":", hypothesis_dist[i], ",", hypothesis[i])

    pass


history_pre = random.choices([0, 1, 2, 3], weights=true, k=50)
history_post= random.choices([0, 1, 2, 3], weights=pred, k=50)

history_comb = history_pre + history_post

calc_trajectory(history_comb)
# print(calc_prob(history_pre))
# print(calc_prob(history_post))
# for i in range(0, 51, 10):
#     calc = calc_prob(history_comb[i:i+50])
#     distance = model_distance(true, calc)
    # print(i, calc, distance)
