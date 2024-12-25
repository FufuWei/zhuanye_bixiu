#首先导入实验所需的包
from kanren import *
from kanren.core import lall
import time


def left(q, p, list): #关系集合list中q在p的右侧
    return membero((q, p), zip(list, list[1:]))

def next(q, p, list): #借助left(),a在b左边或b在a左边
    return conde([left(q, p, list)], [left(p, q, list)])
#根据已知条件的性质将条件分为几组，首先有着确定关系的实体和其属性的条件
#以及同属于一个实体的属性间的关系
houses = var() #创建逻辑变量house
#使用membero函数表示一个约束,membero(item,coll)表示item是coll集合中的一个成员

rules_zebraproblem = lall((eq, (var(), var(), var(), var(), var()), houses),

#def define_rules(houses):
 #   rules_zebraproblem = lall((eq, (var(), var(), var(), var(), var()), houses)),

#var() order: country,job,drinks,pet,color
(membero, ('Britain', var(), var(), var(), 'red'), houses),  #英国人住在红房子里
(membero, ('Spain', var(),var(),'dog',var()), houses), #西班牙人养了一条狗
(membero, ('Japan', 'painter', var(), var(),var()), houses), #意大利人喝茶
(membero, ('Italy', var(), 'tea', var(), var()),houses), #摄影师养了一只蜗牛
(membero, (var(), 'Photographer', var(), 'snail', var()), houses),  #摄影师养了一只蜗牛
(membero, (var(), 'diplomat', var(), var(), 'yellow'), houses), #外交官住在黄房子里
(membero, (var(), var(), 'coffee', var(), 'green'), houses), #喜欢和咖啡的人住在绿房子
(membero, (var(), 'Violinist', 'juice', var(), var()), houses), #小提琴家喜欢喝橘子汁

#实体在整体中确切属性
#eq函数，eq(a,b)表示ab相等

 (eq, (('Norwegian', var(), var(), var(), var()), var(), var(), var(), var()), houses),  #
 (eq, (var(), var(), (var(), var(), 'milk', var(), var()), var(), var()), houses),  #中间房子的人喜欢喝牛奶

#描述两个实体间的不确定关系表达式
#zip()函数将可迭代的对象作为参数，将对象中对应元素打包成一个个元组，返回由这些元组组成的列表
#CONDE用于逻辑和/或的目标构造函数


 (left, #绿房子在白房子右边
  (var(), var(), var(), var(), 'green'),
  (var(), var(), var(), var(), 'white'),
  houses),

 (next, #挪威人住在蓝色房子旁边
  ('Norwegian', var(), var(), var(), var()),
  (var(), var(), var(), var(), 'blue'),
  houses),

 (next,#养狐狸的人所住的房子与医生房子相邻
  (var(), 'physicain', var(), var(), var()),
  (var(), var(), var(), 'fox', var()),
  houses),

 (next,#养马的人所住的房子与外交官的房子相邻
  (var(), 'diplomat', var(), var(), var()),
  (var(), var(), var(), 'horse', var()),
  houses),

 (membero, (var(), var(), var(), 'zebra', var()), houses),  #有人养斑马
 (membero, (var(), var(), 'water', var(), var()), houses))  #有人喝水


solutions = run(0, houses, rules_zebraproblem)

if len(solutions):
    zebra_owner = ""
    water_drinker = ""
    for i in solutions[0]:
        if "zebra" in i:
            zebra_owner = i[0]
        if "water" in i:
            water_drinker = i[0]
        print(i)

    print('\nzebra_owner:\t\t' + zebra_owner)
    print('water_drinker:\t' + water_drinker)

else:
    print("no answer")







