'''def make_pretty(func):

    def inner():
        print("I got decorated")
        func()
    return inner

@make_pretty
def ordinary():
    print("I am ordinary")

ordinary()
'''


'''def make_pretty(func):
    def inner():
        print("I got decorated")
        func()
    return inner

def ordinary():
    print("I am ordinary")

decorated_func = make_pretty(ordinary)

decorated_func()'''

x = [0.0] * 3
print(x)
