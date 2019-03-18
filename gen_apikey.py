#!/usr/bin/env python

import random
import string

def main():
    length = 64
    print( ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length)) )


if __name__ == "__main__":
    main()
