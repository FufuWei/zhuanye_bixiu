### 练习
#### 练习1：理解first-fit 连续物理内存分配算法（思考题）
first-fit 连续物理内存分配算法作为物理内存分配一个很基础的方法，需要同学们理解它的实现过程。请大家仔细阅读实验手册的教程并结合`kern/mm/default_pmm.c`中的相关代码，认真分析default_init，default_init_memmap，default_alloc_pages， default_free_pages等相关函数，并描述程序在进行物理内存分配的过程以及各个函数的作用。
请在实验报告中简要说明你的设计实现过程。请回答如下问题：
- 你的first fit算法是否有进一步的改进空间？

1. 理解已给的`first_fit`算法

1.1. `default_init`：
初始化free list

![图片](initial.png)

1.2. `default_init_memmap`：
    
```
/*
1.初始化n个page
2.设置head page的PageProperty标志，更新其property，和free list中的free page数
3.按照地址大小顺序将初始化的free page插入free list

*/
```

![图片](init.png)

1.3. `default_alloc_pages`
```
/*
1. 判断剩余空间是否足够
2.若足够，在free list中找到第一个满足分配需求的page
3.若该page分配后仍有空余，则将剩余free page加入free list，并更新head page和对应的PageProperty
4.更新free list中的free page数量，清空旧head page的Pageproperty位

*/

```

![图片](alloc.png)

1.4. `default_free_pages`
```
/*
1.将要释放的page中的置位与引用次数清空
2.根据释放大小更新nr_free,确定释放的head page
3.将释放的free page按照地址大小加入链表
4.合并与之相邻的可合并的free page并更新相应参数
*/

```
![图片](free1.png)

![图片](free2.png)

2. 该`first_fit`算法的改进空间：

2.1. free page时的合并算法：

没有循环考虑合并后的相邻空闲块是否可以继续合并

#### 练习2：实现 Best-Fit 连续物理内存分配算法（需要编程）
在完成练习一后，参考kern/mm/default_pmm.c对First Fit算法的实现，编程实现Best Fit页面分配算法，算法的时空复杂度不做要求，能通过测试即可。
请在实验报告中简要说明你的设计实现过程，阐述代码是如何对物理内存进行分配和释放，并回答如下问题：
- 你的 Best-Fit 算法是否有进一步的改进空间？

##### Best-Fit分配算法：将free list中的free block按照大小顺序和地址顺序排序，每次从free list中找到最小的符合分配需求的空闲块。

##### 参照了first-fit算法进行了实现：

###### 对物理内存进行分配：

1. 首先判断剩余的free block是否满足需求

2. 如果满足，遍历空闲链表，找到最小的满足需求的free page，{通过记录上一个满足要求的free page，与当前满足要求的free page大小进行比较，留下较小的一个}

3. 若分配后仍有空余，将剩余部分插入链表并设置新的head page的标记位和property(块中空闲页的数目)；清空旧head page的标记位

###### 对物理内存进行释放：

1. 首先将要释放的内存页的标记位重置，设置head page的property以及标记位，更新nr_free

2. 将要释放的页插入free list

3. 若插入的空闲页与相邻页可以合并，就进行循环合并

考虑到由于实现的算法在回收空闲页的时候没有更改其位置，所以在查找时需要遍历free list，找到最小符合要求的free page然后返回

参见源代码处
