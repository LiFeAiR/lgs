import random, time


def sleep(min=50, max=1000):
    random_number = random.randint(min, max)
    time.sleep(0.001 * random_number)
