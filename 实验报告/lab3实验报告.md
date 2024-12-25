# lab3实验报告

## 练习1：理解基于FIFO的页面替换算法

当程序触发页异常的时候，会进入对应的处理程序 `pgfault_handler` 函数，在此函数中会调用 `print_pgfault` 打印一些错误信息，以及将这些错误信息交给 `do_pgfault` 函数处理。

> `do_pgfault` 函数原型如下所示：
>
> ```c
> int do_pgfault(struct mm_struct *mm, uint_t error_code, uintptr_t addr)
> `do_pgfault` 是处理函数的主体，在此函数中进行页面的换入换出等操作。

在 `do_pgfault` 函数调用过程中首先会调用 `find_vma` 函数。

> `find_vma` 函数会在 `vma` 结构体链表中找到一个满足 `vma->vm_start<=addr && addr < vma->vm_end` 条件的 `vma` 结构体。
>
> 此处是检测地址是否合法。

在调用 `find_vma` 检测地址合法后会调用 `get_pte` 函数。

>```c
>pte_t *get_pte(pde_t *pgdir, uintptr_t la, bool create) {
>pde_t *pdep1 = &pgdir[PDX1(la)]; // 获取二级页表目录
>if (!(*pdep1 & PTE_V)) { // 检查是否合法
>   struct Page *page;
>   if (!create || (page = alloc_page()) == NULL) {
>       return NULL;
>   }
>   set_page_ref(page, 1);
>   uintptr_t pa = page2pa(page);
>   memset(KADDR(pa), 0, PGSIZE);
>   *pdep1 = pte_create(page2ppn(page), PTE_U | PTE_V);
>}
>pde_t *pdep0 = &((pde_t *)KADDR(PDE_ADDR(*pdep1)))[PDX0(la)]; // 找到一级页表目录项
>if (!(*pdep0 & PTE_V)) {
>	struct Page *page;
>	if (!create || (page = alloc_page()) == NULL) {
>		return NULL;
>	}
>	
>	set_page_ref(page, 1);
>	uintptr_t pa = page2pa(page);
>	memset(KADDR(pa), 0, PGSIZE);
>	*pdep0 = pte_create(page2ppn(page), PTE_U | PTE_V);
>}
>return &((pte_t *)KADDR(PDE_ADDR(*pdep0)))[PTX(la)]; // 返回一级页表页表项
>}
>```
>
>` get_pte` 函数会根据得到的虚拟地址，在三级页表中进行查找。在查找页表项的时候，如果页表项无效的话会给页表项分配一个全是0的页并建立映射。最后返回虚拟地址对应的一级页表的页表项。

获取了 `pte` 以后，会检测此页表项是否有对应的页面。

如果页表项全零，这个时候就会调用 `pgdir_alloc_page` 。

在 `pgdir_alloc_page` 首先会调用 `alloc_page` 函数。`alloc_page` 函数则是调用了 `alloc_pages(1)` ,此函数原型如下所示：

```c
struct Page *alloc_pages(size_t n) {
    struct Page *page = NULL;
    bool intr_flag;

    while (1) {
        local_intr_save(intr_flag);
        { page = pmm_manager->alloc_pages(n); }
        local_intr_restore(intr_flag);

        if (page != NULL || n > 1 || swap_init_ok == 0) break;

        extern struct mm_struct *check_mm_struct;
        swap_out(check_mm_struct, n, 0);
    }
    return page;
}
```

在 `alloc_pages` 函数中，首先是根据物理页面分配算法给自身发呢配一个物理页面，然后会调用 `swap_out` 函数。 

`swap_out` 函数则是会根据页面置换算法选择出一个应该换出的页面并写入到磁盘中，并将此页面释放。

> `swap_out` 函数找到应该换出的页面则是通过 `swap_out_victim` 实现的。
>
> ```C
> static int _fifo_swap_out_victim(struct mm_struct *mm, struct Page ** ptr_page, int in_tick)
> {
>   list_entry_t *head=(list_entry_t*) mm->sm_priv;
>       assert(head != NULL);
>   assert(in_tick==0);
>  list_entry_t* entry = list_prev(head);
>  if (entry != head) {
>      list_del(entry);
>      *ptr_page = le2page(entry, pra_page_link);
>  } else {
>      *ptr_page = NULL;
>  }
>  return 0;
> }
> ```
>
> 这个函数是基于FIFO的页面替换算法的核心。根据此算法的思想，在页面置换中，我们需要换出的是最先使用的页面，也就是最先加入到链表的节点对应的页面。在链表中，最先加入页面对应的节点就是头节点 `head` 的上一个，调用 `list_prev` 即可。

> 将页面内容写入磁盘则是通过磁盘的写函数实现的。在 `kern/fs/swapfs.c` 中封装了磁盘的读入写出函数。
>
> ```c
> int // 此函数封装了磁盘的读操作。
> swapfs_read(swap_entry_t entry, struct Page *page) {
>  return ide_read_secs(SWAP_DEV_NO, swap_offset(entry) * PAGE_NSECT, page2kva(page), PAGE_NSECT);
> }
> ```
>
> ```c
> int // 此函数封装了磁盘的读操作。
> swapfs_write(swap_entry_t entry, struct Page *page) {
>  return ide_write_secs(SWAP_DEV_NO, swap_offset(entry) * PAGE_NSECT, page2kva(page), PAGE_NSECT);
> }
> ```

在 `pgdir_alloc_page` 调用 `alloc_page` 获得分配的页面后会调用 `page_insert` 函数。

> `page_insert` 函数则是将虚拟地址和页面之间建立映射关系。
>
> 在此函数中首先会用 `get_pte` 获取页表项。然后会判断页表项对应的页面和要建立映射的页面是否相同。
>
> 不同的话会调用 `page_remove_pte` 函数将此页表项失效。接着会调用 `pte_create` 函数建立新的页表项比那个将其赋值给 `get_pte` 找到的页表项的地址。

>  `page_remove_pte` 执行时会找到 `pte` 对应的页面，减少其引用，并将页面释放。 

> ```c
> static inline pte_t pte_create(uintptr_t ppn, int type) {
>  return (ppn << PTE_PPN_SHIFT) | PTE_V | type;
> }
> ```
>
> `pte_create` 则是直接根据物理页号进行偏移并对标志位进行设置完成。

然后 `pgdir_alloc_page` 会调用 `swap_map_swappable` 函数。

> `swap_map_swappable` 则是将页面加入相应的链表，设置页面可交换。



如果 `do_pgfault` 函数获取 `addr` 函数对应的 `pte` 不为空的话，则首先会调用 `swap_in` 函数。

> `swap_in` 函数的作用是分配一个页面并从磁盘中将相应的值写入到此页面上

然后会调用 `page_insert` 函数进行页面的映射以及调用 `swap_map_swappable` 则是将页面加入相应的链表，设置页面可交换。





## 练习2：深入理解不同分页模式的工作原理（思考题）

#### get_pte()函数中有两段形式类似的代码， 结合sv32，sv39，sv48的异同，解释这两段代码为什么如此相像。

因为get_pte()函数的逻辑是类似于一个递归向下寻找页表项的过程，根据PDX1和三级页表PDE找到二级页表PDE，再结合PDX0，找到一级页表PDE，根据PTX找到PTE。

- **如果页表项有效**：说明已经存在一个合适的页表，函数返回该页表项的地址。
- **如果页表项无效**：
  - 如果当前处理的是最底层的页表级别，表示已经到达页表的叶子级别，需要创建一个新的页表项，并将其添加到当前页表中。
  - 如果当前处理的不是最底层的页表级别，表示需要继续往下一级的页表查找或创建。函数会继续向下寻找，在下一级的页表上执行相同的操作。

这两段代码相似的原因是，不论是处理 `sv32`、`sv39` 还是 `sv48` 的页表，它们的基本结构和操作逻辑是相似的。不同的只是地址空间大小和页表的层次结构。因此，为了处理不同的地址空间大小，可以重用类似的代码结构，仅仅根据具体的需求调整页表项的大小和页表的层次结构。



#### 目前get_pte()函数将页表项的查找和页表项的分配合并在一个函数里，你认为这种写法好吗？有没有必要把两个功能拆开？

好。目前阶段没有必要将两个功能拆开，因为当前阶段的页表结构比较简单，并且逻辑清晰，在通过get_pte()进行页表项的查找和页表项的分配时执行逻辑流程都相对简单，并且合并在一个函数可以减少函数调用，简化代码逻辑，减少开销提高性能。



## 练习3：给未被映
射的地址映射上物理页

#### 请描述页目录项（Page Directory Entry）和页表项（Page Table Entry）中组成部分对ucore实现页替换算法的潜在用处。

PTE_A和PTE_D分别代表了内存页是否被访问过和内存也是否被修改过，借助这两个标志位，可以实现进阶时钟页替换算法。



#### 如果ucore的缺页服务例程在执行过程中访问内存，出现了页访问异常，请问硬件要做哪些事情？

当出现页访问异常时，硬件首先会将错误的相关信息保存在相应寄存器中，并且将执行流程转交给中断处理程序。



#### 数据结构Page的全局变量（其实是一个数组）的每一项与页表中的页目录项和页表项有无对应关系？如果有，其对应关系是啥？

page数组中的每一项都对应了一个页面，page的vaddr属性存储了页面虚拟地址，通过虚拟地址可以获得页目录项和页表项。



## 练习4：补充完成Clock页替换算法

#### clock页替换算法实现过程
1.将clock页替换算法所需数据结构进行初始化。
```
_clock_init_mm(struct mm_struct *mm)
{
    list_init(&pra_list_head);
    curr_ptr = &pra_list_head;
    mm->sm_priv = &pra_list_head;
    return 0;
}
```

2.将页面`page`插入到页面链表`pra_list_head`的末尾并将页面的`visited`标志置为1，表示该页面已被访问。
```
_clock_map_swappable(struct mm_struct *mm, uintptr_t addr, struct Page *page, int swap_in)
{
    list_entry_t *entry = &(page->pra_page_link);
    list_entry_t *head = (list_entry_t *)mm->sm_priv;
    assert(entry != NULL && curr_ptr != NULL);
    list_add(head, entry);
    page->visited = 1;
    curr_ptr = entry;
    cprintf("curr_ptr %p\n", curr_ptr);
    return 0;
}
```
3.通过`tmp`指针遍历页面链表，找到一个`visited`为0即未被访问的页面。若找到了此页面，将该页面从链表中删除，并将其地址存储在`ptr_page`作为换出页面。若当前页面已被访问，则将`visited`标志置为0，表示该页面已被重新访问。


```
_clock_swap_out_victim(struct mm_struct *mm, struct Page **ptr_page, int in_tick)
{
    list_entry_t *head = (list_entry_t *)mm->sm_priv;
    assert(head != NULL);
    assert(in_tick == 0);
    list_entry_t *tmp = head;
    while (1)
    {
        list_entry_t *entry = list_prev(tmp);
        struct Page *p = le2page(entry, pra_page_link);
        if (p->visited == 0)
        {
            list_del(entry);
            *ptr_page = p;
            cprintf("curr_ptr %p\n", curr_ptr);
            break;
        }
        else
            p->visited = 0;
        tmp = entry;
    }
    return 0;
}
```

#### 比较Clock页替换算法和FIFO算法的不同
- **FIFO页替换算法：** 根据页面进入内存的先后顺序进行替换，即最早进入内存的页面先被替换。使用队列数据结构来维护页面的进入顺序，不考虑页面的访问频率，且存在Belady现象。
- **clock页替换算法：** 时钟页替换算法把各个页面组织成环形链表的形式，每个页面都有一个引用位，当页面被访问时，引用位被设置为1，当需要替换页面时，从当前位置开始查找引用位为0的页面进行替换。其在使用过程中需要维护一个循环链表，并且需要更新页面的引用位，实现起来相对复杂。但其考虑页面的访问频率，且不存在Belady现象，性能更加优秀。





## 练习5：阅读代码和实现手册，理解页表映射方式相关知识

#### 如果我们采用”一个大页“ 的页表映射方式，相比分级页表，有什么好处、优势，有什么坏处、风险？

**优势**：

1. 性能提升：大页表映射方式可以降低页表的层次深度，减少了虚拟地址到物理地址的映射查找次数，从而提高了内存访问速度。这对于大型内存数据库、科学计算和虚拟机等应用程序可能特别有利。
2. TLB 命中率提高：大页表可以提高 TLB的命中率，因为更多的虚拟地址范围映射到相同的物理页帧上，从而减少了 TLB 缓存失效的机会。
3. 减少页表条目数量：大页表可以减少需要维护的页表条目数量，这对于操作系统内核的性能和效率来说是有益的。减少页表的大小也可以减少内存消耗。

**坏处**：

1. 内存浪费：使用大页表时，每个页面都会较大，因此可能会浪费一定的内存空间，尤其是对于小型数据结构或小程序来说。
2. 内存碎片：大页表映射方式可能导致更多的内存碎片，因为大页表必须保持连续的物理地址范围，这可能限制了内存的动态分配和回收能力。
3. 不适用于非连续内存需求：如果应用程序需要在内存中分配非连续的虚拟地址范围，大页表映射方式可能会变得不够灵活。