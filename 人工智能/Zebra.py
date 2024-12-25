#首先导入实验所需的包
from kanren import *
from kanren.core import lall



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
(membero, ('英国人', var(), var(), var(), '红色'), houses),  #英国人住在红房子里
(membero, ('西班牙人', var(), var(), '狗', var()), houses), #西班牙人养了一条狗
(membero, ('日本人', '油漆工', var(), var(), var()), houses), #意大利人喝茶
(membero, ('意大利人', var(), '茶', var(), var()), houses), #摄影师养了一只蜗牛
(membero, (var(), '摄影师', var(), '蜗牛', var()), houses),  #摄影师养了一只蜗牛
(membero, (var(), '外交官', var(), var(), '黄色'), houses), #外交官住在黄房子里
(membero, (var(), var(), '咖啡', var(), '绿色'), houses), #喜欢和咖啡的人住在绿房子
(membero, (var(), '小提琴家', '橘子汁', var(), var()), houses), #小提琴家喜欢喝橘子汁

#实体在整体中确切属性
#eq函数，eq(a,b)表示ab相等

 (eq, (('挪威人', var(), var(), var(), var()), var(), var(), var(), var()), houses),  #
 (eq, (var(), var(), (var(), var(), '牛奶', var(), var()), var(), var()), houses),  #中间房子的人喜欢喝牛奶

#描述两个实体间的不确定关系表达式
#zip()函数将可迭代的对象作为参数，将对象中对应元素打包成一个个元组，返回由这些元组组成的列表
#CONDE用于逻辑和/或的目标构造函数


 (left, #绿房子在白房子右边
  (var(), var(), var(), var(), '绿色'),
  (var(), var(), var(), var(), '白色'),
  houses),

 (next, #挪威人住在蓝色房子旁边
  ('挪威人', var(), var(), var(), var()),
  (var(), var(), var(), var(), '蓝色'),
  houses),

 (next,#养狐狸的人所住的房子与医生房子相邻
  (var(), '医生', var(), var(), var()),
  (var(), var(), var(), '狐狸', var()),
  houses),

 (next,#养马的人所住的房子与外交官的房子相邻
  (var(), '外交官', var(), var(), var()),
  (var(), var(), var(), '马', var()),
  houses),

 (membero, (var(), var(), var(), '斑马', var()), houses),  #有人养斑马
 (membero, (var(), var(), '矿泉水', var(), var()), houses))  #有人喝水


solutions = run(0, houses, rules_zebraproblem)

 # 解算器的输出结果展示
print("所有结果如下:")
for i in solutions[0]:
 print(i)

 # 提取解算器的输出
output = [house for house in solutions[0] if '斑马' in house][0][4]
print('\n{}房子里的人养斑马'.format(output))
output = [house for house in solutions[0] if '矿泉水' in house][0][4]
print('\n{}房子里的人喜欢喝矿泉水\n'.format(output))









