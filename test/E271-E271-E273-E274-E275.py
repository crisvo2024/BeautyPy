# from, import, as keywords:
from .	   import		  africa 	 	as AFRICA,     europa, america, asia

# import keyword:
import collections	  	,		 	os		,		wave

# def, return(mirar la indentación antes) keywords:
def       func():
    if 1          in         [1, 2, 3]:
        return 	 		 	 	 	"BeautyPy!!!!"

# del keyword:
my_var = 5
my_tuple = ('Sam', 25)
my_dict = {'name': 'Sam', 'age': 25}

del 				 my_var
del my_tuple
del 	 	 	 	my_dict

# raise, from, as keywords:
def func():
    raise 		  	IOError
    try:
        func()
    except IOError as exc:
        raise 	  		 	RuntimeError('Failed to open database') 	 	from    	exc

# global keyword:
c = 0
j = 1

def add():
    global 	  	  		c   ,	j
    c=c 		+ 2 -	j
    print ("Inside add():", c )

add()
print("In main:", c)

# nonlocal keyword:
def  myfunc1():
	x= "John"
	def myfunc2():
		nonlocal 	 x,y
		x = "BeautyPy!!!!"
	myfunc2()
	return  x

# assert keyword:
x = "hello"
assert   	x=="goodbye","x should be 'hello'"

# async, await keywords:
async 	  	def count():
    print("One")
    await asyncio.sleep(1)
    print("Two")

# if, elif, else keywords:
num = 3.4
if 	  	num> 0	:
    print("Positive number")
elif      num 	== 	 0:
    print("Zero")
else			:
    print		("Negative number")

# while ketword: 
counter = 0
while 		counter < 3:
    print("Inside loop")
    counter=counter + 1
else:
    print("Inside else")

# for keyword:
for 		i 		in range(1, 4): 
    print(i) 
else	:  # Executed because no break in for 
    print("BeautyPy!!!")