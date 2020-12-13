import math
op          =           1
op          +=op     *2         //7 +   8    **   3 +   3-7
op-=            op*8 +  8       %144    /87   -         9
op                  *=  77*         5-      op   *77   -    4**9    //11
op              /=      8       //op*2-8-7-9+89
op              %=op**2         +   54      -7  +   77+96
op//=               op//        78
op          **=     4+5+6-      9   -   op//    88  /       2    **     2
op=int(op)
op&=                    8 -         7       +       9
op      |=op        +2
op              ^=                  op       -      9    +      5
op            >>=       99      *     abs(op)               -  7
op <<=              op*2        +               5       *14

x=50
if op<-26551651:
    x=                 0
elif op>            -110201:
    x            =1
elif op         ==0:
    x = 2
elif op>=               -110201 :
    x = 3
elif op<=  -1102             :
    x=4
elif op !=          -8:
    x =         5

a =                  5
b                =           [3,8,4,6]
if a in                 b:
    x        =              6
elif a          not in b            :
    x           =7
elif a is                  b    :
    x=8
elif a   is not     b:
    x=                  9

w = True
y = False
z = False
if w                    and         y             :
    x = 10
elif w      or          y:
    x = 11
elif      not           y or            w and       not     z:
    x = 12
else:
    x= 13

a = 60
b = 13
c = 0

c = a&b

c    =a       |b

c = a ^         b

c=a       <<              2

c = a               >>2
