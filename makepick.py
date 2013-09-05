#!/usr/bin/env python
import random
import time


def main():
    random.seed(time.time())
    score = random.random()
    if score > 0.55:
        print "AWAY"
    else:
        print "HOME"


if '__main__' == __name__:
    main()
