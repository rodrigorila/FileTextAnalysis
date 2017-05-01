# TIPS:
#  - enumerate returns tuples: index, item of a list: enumrate(['a', 'b', 'c']) -> (0, 'a') (1, 'b') (2, 'c')
#  - zip: returns tuples of two or more lists paired together: zip(['a', 'b', 'c'], [7, 8, 2 ]) -> ('a', 7) ('b', 8) ('c', 2)
#  - swap values using tuples packing-unpacking: x, y = y, x
#  - else: in for loops means "if no break was called" during the loop (it works for loops that use break
#  - else: in try-except excecutes code that didn't failed
#  - map: use it to call a function on a list of values and get the list of return values




# Closures
#
# def xmlElement(tagName):
#     tag = tagName
#     def write(value):
#         print "<"+tag+">"+value+"</"+tag+">"
#
#     return write
#
# cut = xmlElement("cut")
# blow = xmlElement("blow")
#
# cut("roses")
# blow("noses")
# cut("the bullshit")
# blow("in my hair")
#
#
# CALL LOGGER
#
# def callLogger(func):
#     def execute(*args):
#         result = func(*args)
#         print "Executed: %s%s -> %s" % (func.__name__, args, result)
#
#     return execute
#
# def add (a, b):
#     return a + b
# def sub (a, b):
#     return a - b
#
# addLog = callLogger(add)
# subLog = callLogger(sub)
#
# addLog(1, 1)
# subLog(7, 3)
# addLog(8, 10.7)
# subLog(3.14, 1.17)
#
#
# def letra(num):
#     return chr(96+num)
# nombres = map(letra, [1, 5, 3, 9])
# nombres = map(lambda x: chr(64 + x), [1, 5, 3, 9])
#
# print list(nombres)
# sys.exit(0)
#

# file = os.path.join('Numbers', 'More than 10 MB.txt')
# x = 0
# for c in gt.files.fileChars(file):
#     x += 1
# print x

# def charsOfFile(file):
#     with open(file, "rb") as f:
#         while True:
#             chunk = f.read(512 * 1024 * 1024 )
#             if chunk:
#                 for c in chunk:
#                     yield c
#
#             else:
#                 break
# file = os.path.join('Numbers', 'More than 10 MB.txt')
# x = 0
# for c in charsOfFile(file):
#     x += 1
# print x


# def charsOfFile(file):
#     with open(file, "rb") as f:
#         while True:
#             chunk = f.read(128 * 1024 * 1024 )
#             if chunk:
#                 for c in chunk:
#                   yield c
#             else:
#                 break
# file = os.path.join('Numbers', 'More than 10 MB.txt')
# x = 0
# for c in charsOfFile(file):
#     x += 1
# print x



# def charsOfFile(file, process):
#     with open(file, "rb") as f:
#         while True:
#             chunk = f.read(128 * 1024 * 1024 )
#             if chunk:
#                 for c in chunk:
#                     process(c)
#             else:
#                 break
# file = os.path.join('Numbers', 'More than 10 MB.txt')
# x = 0
# def addx(c):
#     global x
#     x += 1
# charsOfFile(file, addx)
# print x



# file = os.path.join('Numbers', 'More than 10 MB.txt')
# x = 0
# with open(file, "rb") as f:
#     while True:
#         chunk = f.read(128 * 1024 * 1024)
#         if chunk:
#             for c in chunk:
#                 x += 1
#         else:
#             break
# print x

# def calculate(gen):
#     t = 0
#     for g in gen():
#         t += g
#
#     return t
#
# def printg(gen):
#     for g in gen():
#         print g
#
# def gen():
#     for i in range(0, 10):
#         yield i
#
# x = gen
#
# print calculate(x)
# printg(x)


# from time import sleep
# import sys
# for i in range(21):
#     sys.stdout.write('\r')
#     # the exact output you're looking for:
#     sys.stdout.write("[%-20s] %d%%" % ('='*i, 5*i))
#     sys.stdout.flush()
#     sleep(0.25)
# print

# file, mask  = "algo.exe\h02DC", "*.*\h02DC"
#
# if (fnmatch.fnmatchcase(file, mask)):
#     print "OK"
# else:
#     print "FAIL"

