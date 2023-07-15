'''def make_pretty(func):

    def inner():
        print("I got decorated")
        func()
    return inner

@make_pretty
def ordinary():
    print("I am ordinary")

ordinary()



def make_pretty(func):
    def inner():
        print("I got decorated")
        func()
    return inner

def ordinary():
    print("I am ordinary")

decorated_func = make_pretty(ordinary)

decorated_func()
'''

def smart_divide(func):
    def inner(*args):
        print("I am going to divide", args[0], "and", args[1])
        if args[1] == 0:
            print("Whoops! cannot divide")
            return

        return func(*args)
    return inner

@smart_divide
def divide(*args):
    print(args[0]/args[1])

divide(2,5)

divide(2,0)


'''def divide(a, b):
    print(a/b)

decorated_func = smart_divide(divide)

decorated_func(2, 5)'''

'''divide(2,5)

divide(2,0)'''
