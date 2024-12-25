第一个问题是idleproc 是怎么创建的，这个通过init.c文件中的proc _init函数(这个得详细解释）创建的，并且idleproc创建之后没有在运行，

第二个问题是解释kernel_thread函数解释，会问到tf.epc和tf.status，

第三个问题是解释do_fork函数，

第四个问题是proc_state有哪些，和切换上下文用到的switch_to函数（一个是把上文寄存的值写到内存中，一个是把新进程的值从内存中读到寄存器中），

然后解释getpid()函数，

最后一个是解释proc_run函数，lcr3(next->cr3)中
cr3的值在lab4中只有一个，所有内核线程的内核虚地址空间（也包括物理地址空间）是相同的，既内核线程共用一个映射内核空间的页表

##练习1：分配并初始化一个进程控制块（需要编码）
alloc_proc函数（位于kern/process/proc.c中）负责分配并返回一个新的struct proc_struct结构，用于存储新建立的内核线程的管理信息。ucore需要对这个结构进行最基本的初始化，你需要完成这个初始化过程。

【提示】在alloc_proc函数的实现中，需要初始化的proc_struct结构中的成员变量至少包括：state/pid/runs/kstack/need_resched/parent/mm/context/tf/cr3/flags/name。

请在实验报告中简要说明你的设计实现过程。请回答如下问题：



struct proc_struct {
    enum proc_state state;                      // Process state
    int pid;                                    // Process ID
    int runs;                                   // the running times of Proces
    uintptr_t kstack;                           // Process kernel stack
    volatile bool need_resched;                 // bool value: need to be rescheduled to release CPU?
    struct proc_struct *parent;                 // the parent process
    struct mm_struct *mm;                       // Process's memory management field
    struct context context;                     // Switch here to run process
    struct trapframe *tf;                       // Trap frame for current interrupt
    uintptr_t cr3;                              // CR3 register: the base addr of Page Directroy Table(PDT)
    uint32_t flags;                             // Process flag
    char name[PROC_NAME_LEN + 1];               // Process name
    list_entry_t list_link;                     // Process link list 
    list_entry_t hash_link;                     // Process hash list
};

enum proc_state state：进程的状态，采用枚举类型proc_state表示，可以是就绪、运行、等待等状态。
int pid：进程的唯一标识符，即进程ID。
int runs：进程的运行次数。
uintptr_t kstack：进程的内核栈的地址。
volatile bool need_resched：表示进程是否需要重新调度来释放CPU的布尔值。
struct proc_struct *parent：指向父进程的指针。
struct mm_struct *mm：进程的内存管理结构。
struct context context：用于保存进程的上下文信息，用于切换到该进程运行。
struct trapframe *tf：当前中断的陷阱帧。
uintptr_t cr3：CR3寄存器，存储页目录表（Page Directory Table）的基地址。
uint32_t flags：进程的标志位。
char name[PROC_NAME_LEN + 1]：进程的名称，长度为PROC_NAME_LEN + 1。
list_entry_t list_link：用于将进程链接到进程链表中的链表节点。
list_entry_t hash_link：用于将进程链接到进程哈希表中的链表节点。


// alloc_proc - alloc a proc_struct and init all fields of proc_struct
static struct proc_struct *
alloc_proc(void) {
    struct proc_struct *proc = kmalloc(sizeof(struct proc_struct));
    if (proc != NULL) {
    //LAB4:EXERCISE1 YOUR CODE
    /*
     * below fields in proc_struct need to be initialized
     *       enum proc_state state;                      // Process state
     *       int pid;                                    // Process ID
     *       int runs;                                   // the running times of Proces
     *       uintptr_t kstack;                           // Process kernel stack
     *       volatile bool need_resched;                 // bool value: need to be rescheduled to release CPU?
     *       struct proc_struct *parent;                 // the parent process
     *       struct mm_struct *mm;                       // Process's memory management field
     *       struct context context;                     // Switch here to run process
     *       struct trapframe *tf;                       // Trap frame for current interrupt
     *       uintptr_t cr3;                              // CR3 register: the base addr of Page Directroy Table(PDT)
     *       uint32_t flags;                             // Process flag
     *       char name[PROC_NAME_LEN + 1];               // Process name
     */

	proc->state = PROC_UNINIT;
    proc->pid = -1; 
    proc->runs = 0;
    proc->kstack = 0;
    proc->need_resched = 0;
    proc->parent = NULL;
    proc->mm = NULL;
    memset(&(proc->context), 0, sizeof(struct context));
    proc->tf = NULL;
    proc->cr3 = 0;
    proc->flags = 0;
    memset(proc->name, 0, sizeof(proc->name));


    }
    return proc;
}

请说明**proc_struct中struct context context和struct trapframe *tf**成员变量含义和在本实验中的作用是啥？（提示通过看代码和编程调试可以判断出来）

struct context context定义：
struct context {
    uintptr_t ra;
    uintptr_t sp;
    uintptr_t s0;
    uintptr_t s1;
    uintptr_t s2;
    uintptr_t s3;
    uintptr_t s4;
    uintptr_t s5;
    uintptr_t s6;
    uintptr_t s7;
    uintptr_t s8;
    uintptr_t s9;
    uintptr_t s10;
    uintptr_t s11;
};

结构体中包含了14个uintptr_t类型的成员变量，分别为ra、sp、s0、s1、s2、s3、s4、s5、s6、s7、s8、s9、s10和s11。这些成员变量用来存储不同寄存器的值，用于保存当前执行环境的上下文信息。

引用：
void switch_to(struct context *from, struct context *to);

// check the proc structure
    int *context_mem = (int*) kmalloc(sizeof(struct context));
    memset(context_mem, 0, sizeof(struct context));
    int context_init_flag = memcmp(&(idleproc->context), context_mem, sizeof(struct context));


struct trapframe {
    struct pushregs gpr;//通用寄存器的值
    uintptr_t status;//处理器状态的值
    uintptr_t epc;//异常程序计数器（Exception Program Counter，EPC）的值，即异常发生时下一条指令的地址
    uintptr_t badvaddr;//出错的虚拟地址
    uintptr_t cause;//导致异常的原因
};



/* *
 * trap - handles or dispatches an exception/interrupt. if and when trap()
 * returns,
 * the code in kern/trap/trapentry.S restores the old CPU state saved in the
 * trapframe and then uses the iret instruction to return from the exception.
 * "trap"是指处理或分发异常或中断的操作。当"trap()"函数返回时，
 * 位于kern/trap/trapentry.S文件中的代码会恢复在trapframe中保存的旧CPU状态，
 * 然后使用iret指令从异常中返回。
 * */
void trap(struct trapframe *tf) {
    // dispatch based on what type of trap occurred
    if ((intptr_t)tf->cause < 0) {
        // interrupts
        interrupt_handler(tf);
    } else {
        // exceptions
        exception_handler(tf);
    }
}

void print_trapframe(struct trapframe *tf) {
    cprintf("trapframe at %p\n", tf);
    print_regs(&tf->gpr);
    cprintf("  status   0x%08x\n", tf->status);
    cprintf("  epc      0x%08x\n", tf->epc);
    cprintf("  badvaddr 0x%08x\n", tf->badvaddr);
    cprintf("  cause    0x%08x\n", tf->cause);
}

/* trap_in_kernel - test if trap happened in kernel */
bool trap_in_kernel(struct trapframe *tf) {
    return (tf->status & SSTATUS_SPP) != 0;
}

// forkret -- the first kernel entry point of a new thread/process
// NOTE: the addr of forkret is setted in copy_thread function
//       after switch_to, the current proc will execute here.
static void
forkret(void) {
    forkrets(current->tf);
}

新线程/进程的第一个内核入口点。在copy_thread函数中设置了forkret的地址，在切换到新线程/进程之后，当前进程将从这里开始执行。

forkret函数内部调用了forkrets函数，并将当前进程的trapframe作为参数传递给forkrets函数。

// copy_thread - setup the trapframe on the  process's kernel stack top and
//             - setup the kernel entry point and stack of process
static void
copy_thread(struct proc_struct *proc, uintptr_t esp, struct trapframe *tf) {
    proc->tf = (struct trapframe *)(proc->kstack + KSTACKSIZE - sizeof(struct trapframe));
//为进程分配一个内核栈空间，并将进程的trapframe结构体指针指向该内核栈的顶部位置。
    *(proc->tf) = *tf;

    // Set a0 to 0 so a child process knows it's just forked
    proc->tf->gpr.a0 = 0;
    proc->tf->gpr.sp = (esp == 0) ? (uintptr_t)proc->tf : esp;

    proc->context.ra = (uintptr_t)forkret;
    proc->context.sp = (uintptr_t)(proc->tf);
}

copy_thread函数会将传入的trapframe结构体复制到进程的内核栈顶部，并设置一些必要的字段。

首先，将proc->tf指向进程的内核栈顶部，即proc->kstack + KSTACKSIZE - sizeof(struct trapframe)。
然后，将传入的trapframe内容拷贝到proc->tf指向的内存位置。
接下来，将proc->tf->gpr.a0设置为0，这样一个子进程就知道自己是刚刚被fork出来的。
将proc->tf->gpr.sp设置为传入的esp值，如果传入的esp为0，则将其设置为proc->tf指向的内存位置。
最后，将proc->context.ra设置为forkret函数的地址，这是进程切换后将执行的第一个内核入口点。
将proc->context.sp设置为proc->tf指向的内存位置，以便在进程切换后正确设置栈指针。
总而言之，这段代码是为了在进程切换后，正确设置进程的trapframe和内核入口点，以及栈指针。


##练习2：为新创建的内核线程分配资源（需要编码）
创建一个内核线程需要分配和设置好很多资源。kernel_thread函数通过调用do_fork函数完成具体内核线程的创建工作。do_kernel函数会调用alloc_proc函数来分配并初始化一个进程控制块，但alloc_proc只是找到了一小块内存用以记录进程的必要信息，并没有实际分配这些资源。ucore一般通过do_fork实际创建新的内核线程。do_fork的作用是，创建当前内核线程的一个副本，它们的执行上下文、代码、数据都一样，但是存储位置不同。因此，我们实际需要"fork"的东西就是stack和trapframe。在这个过程中，需要给新内核线程分配资源，并且复制原进程的状态。你需要完成在kern/process/proc.c中的do_fork函数中的处理过程。它的大致执行步骤包括：

调用alloc_proc，首先获得一块用户信息块。
为进程分配一个内核栈。
复制原进程的内存管理信息到新进程（但内核线程不必做此事）
复制原进程上下文到新进程
将新进程添加到进程列表
唤醒新进程
返回新进程号

/* do_fork -     parent process for a new child process
 * @clone_flags: used to guide how to clone the child process
 * @stack:       the parent's user stack pointer. if stack==0, It means to fork a kernel thread.
 * @tf:          the trapframe info, which will be copied to child process's proc->tf
 * clone_flags：用于指导如何克隆子进程的标志参数。
stack：父进程的用户栈指针。如果stack==0，表示要创建一个内核线程。
tf：陷阱帧信息，将被复制到子进程的proc->tf中。
该函数的功能是创建一个新的子进程，并返回子进程的进程ID。
 */
int
do_fork(uint32_t clone_flags, uintptr_t stack, struct trapframe *tf) {
    int ret = -E_NO_FREE_PROC;
    struct proc_struct *proc;
    if (nr_process >= MAX_PROCESS) {
        goto fork_out;
    }
    ret = -E_NO_MEM;
    //LAB4:EXERCISE2 2110957
    /*
     * Some Useful MACROs, Functions and DEFINEs, you can use them in below implementation.
     * MACROs or Functions:
     *   alloc_proc:   create a proc struct and init fields (lab4:exercise1)
     *   setup_kstack: alloc pages with size KSTACKPAGE as process kernel stack
     *   copy_mm:      process "proc" duplicate OR share process "current"'s mm according clone_flags
     *                 if clone_flags & CLONE_VM, then "share" ; else "duplicate"
     *   copy_thread:  setup the trapframe on the  process's kernel stack top and
     *                 setup the kernel entry point and stack of process
     *   hash_proc:    add proc into proc hash_list
     *   get_pid:      alloc a unique pid for process
     *   wakeup_proc:  set proc->state = PROC_RUNNABLE
     * VARIABLES:
     *   proc_list:    the process set's list
     *   nr_process:   the number of process set
     * alloc_proc：创建一个 proc 结构并初始化字段（lab4:exercise1）
setup_kstack：分配大小为 KSTACKPAGE 的页面作为进程的内核栈
copy_mm：根据 clone_flags，将进程 “proc” 复制或共享进程 “current” 的 mm。如果 clone_flags & CLONE_VM，则 “共享”；否则 “复制”
copy_thread：在进程的内核栈顶设置陷阱帧，并设置进程的内核入口点和堆栈
hash_proc：将 proc 添加到 proc hash_list 中
get_pid：为进程分配一个唯一的 pid
wakeup_proc：将 proc->state 设置为 PROC_RUNNABLE

     * 1、调用alloc_proc函数来分配一个proc_struct结构体，用于表示子进程。
2、调用setup_kstack函数为子进程分配一个内核栈。
3、调用copy_mm函数根据clone_flags来复制或共享父进程的内存管理结构mm。
4、调用copy_thread函数来设置子进程的trapframe和context，以及设置进程的内核入口点和栈。
5、将proc_struct插入到proc hash_list和proc_list中。
6、调用wakeup_proc函数将新的子进程设置为可运行状态。
7、使用子进程的pid来设置ret值，即返回子进程的pid作为函数的返回值。
     */
    

    //    1. call alloc_proc to allocate a proc_struct
    //    2. call setup_kstack to allocate a kernel stack for child process
    //    3. call copy_mm to dup OR share mm according clone_flag
    //    4. call copy_thread to setup tf & context in proc_struct
    //    5. insert proc_struct into hash_list && proc_list
    //    6. call wakeup_proc to make the new child process RUNNABLE
    //    7. set ret vaule using child proc's pid

    proc = alloc_proc();
    if (proc == NULL) {
        goto bad_fork_cleanup_proc;
    }
    
    // 2、call setup_kstack to allocate a kernel stack for child process
    if (!setup_kstack(proc)) {
        goto bad_fork_cleanup_kstack;
    }
    
    // 3、call copy_mm to dup OR share mm according clone_flag
    copy_mm(clone_flags, proc);
    //if (copy_mm(clone_flags, proc) != 0) {
      //  goto bad_fork_cleanup_mm;
    //}
    
    // 4、call copy_thread to setup tf & context in proc_struct
    copy_thread(proc, stack, tf);
    
    // 5、insert proc_struct into hash_list && proc_list
    hash_proc(proc);
    
    // 6、call wakeup_proc to make the new child process RUNNABLE
    wakeup_proc(proc);
    
    // 7、set ret value using child proc's pid
    ret = proc->pid;
    

fork_out:
    return ret;
bad_fork_cleanup_kstack:
    put_kstack(proc);
bad_fork_cleanup_proc:
    kfree(proc);
    goto fork_out;
}


请在实验报告中简要说明你的设计实现过程。请回答如下问题：

请说明ucore是否做到给每个新fork的线程一个唯一的id？请说明你的分析和理由。

每个进程都有一个struct proc_struct结构体表示，其中包含了一个pid_t类型的成员变量pid，用来保存进程的唯一标识符。在进程创建过程中，ucore会为每个新的进程分配一个唯一的pid。

fork是一个操作系统的系统调用，用于创建一个新的进程（子进程）作为调用进程（父进程）的副本。通过fork系统调用，父进程将自己的整个地址空间（包括代码、数据、堆栈等）完全复制给子进程，子进程和父进程在执行fork之后的代码时，会从fork调用之后的位置开始执行。子进程和父进程是相互独立的，它们有着不同的进程ID，可以独立地执行不同的代码路径。

fork系统调用可以使得一个进程分裂为两个并行执行的进程，子进程和父进程可以并行地执行各自的任务。子进程继承了父进程的大部分属性，包括文件描述符、信号处理方式、环境变量等。但是，子进程有自己独立的进程ID。
// get_pid - alloc a unique pid for process为进程分配一个唯一的PID
static int
get_pid(void) {
    static_assert(MAX_PID > MAX_PROCESS);
    struct proc_struct *proc;
    list_entry_t *list = &proc_list, *le;
    //函数内部维护了一个静态变量last_pid，用于记录上一个分配的PID
    static int next_safe = MAX_PID, last_pid = MAX_PID;
    //首先判断last_pid是否已经达到最大值MAX_PID，如果是，则将last_pid重置为1，
    //然后跳转到inside标签处。如果last_pid没有达到最大值，进入inside标签处。
    if (++ last_pid >= MAX_PID) {
        last_pid = 1;
        goto inside;
    }

    if (last_pid >= next_safe) {
    inside:
    //next_safe重置为MAX_PID
        next_safe = MAX_PID;
    repeat:
        le = list;
       // 函数遍历进程链表，查找是否有进程的PID与last_pid相等。
       //如果找到相等的PID，则将last_pid加1，
        while ((le = list_next(le)) != list) {
            proc = le2proc(le, list_link);
            if (proc->pid == last_pid) {
                //如果超过next_safe，则将next_safe重置为MAX_PID，并跳转到repeat标签处重新查找。
                if (++ last_pid >= next_safe) {
                    if (last_pid >= MAX_PID) {
                        last_pid = 1;
                    }
                    next_safe = MAX_PID;
                    goto repeat;
                }
            }
            //如果未找到相等的PID，则判断进程的PID是否大于last_pid，并且小于next_safe，如果是，则将next_safe更新为该进程的PID。
            else if (proc->pid > last_pid && next_safe > proc->pid) {
                next_safe = proc->pid;
            }
        }
    }
    //返回last_pid作为分配的PID
    return last_pid;
}



##练习3：编写proc_run 函数（需要编码）
proc_run用于将指定的进程切换到CPU上运行。它的大致执行步骤包括：

检查要切换的进程是否与当前正在运行的进程相同，如果相同则不需要切换。
禁用中断。你可以使用/kern/sync/sync.h中定义好的宏local_intr_save(x)和local_intr_restore(x)来实现关、开中断。
切换当前进程为要运行的进程。
切换页表，以便使用新进程的地址空间。/libs/riscv.h中提供了lcr3(unsigned int cr3)函数，可实现修改CR3寄存器值的功能。
实现上下文切换。/kern/process中已经预先编写好了switch.S，其中定义了switch_to()函数。可实现两个进程的context切换。
允许中断。

/*
local_intr_save(x) 宏将当前的中断状态保存到变量 x 中，
并在保存完成后立即恢复中断。这样做的目的是为了在一段代码中禁用中断，
执行完后再恢复原来的中断状态。

local_intr_restore(x) 宏用于恢复之前保存的中断状态，
将变量 x 中保存的中断状态恢复到处理器中。
这样做的目的是为了在禁用中断后，恢复到之前的中断状态，以保证系统正常运行。
*/
#define local_intr_save(x) \
    do {                   \
        x = __intr_save(); \
    } while (0)
#define local_intr_restore(x) __intr_restore(x);

/*设置RISC-V处理器的页表寄存器（SPTBR），以指定当前的页表地址。
lcr3函数的参数cr3是一个无符号整数，表示页表的物理地址。
函数内部使用了write_csr宏，将页表地址写入SPTBR寄存器。
SATP32_MODE是一个常量，用于设置SPTBR寄存器的模式位。在这里，它设置了32位地址模式。
RISCV_PGSHIFT也是一个常量，表示每个页的大小的位偏移量。在RISC-V中，页的大小是4KB，所以RISCV_PGSHIFT的值是12。
通过右移操作符将页表地址cr3向右移动RISCV_PGSHIFT位，然后与SATP32_MODE进行按位或运算，最后结果写入SPTBR寄存器。
总结起来，这段代码的作用是将页表的物理地址写入RISC-V处理器的SPTBR寄存器，以指定当前的页表。
*/
static inline void
lcr3(unsigned int cr3) {
    write_csr(sptbr, SATP32_MODE | (cr3 >> RISCV_PGSHIFT));
}


/*
宏定义，用于将一个值写入到指定的控制寄存器（CSR）中。它使用了内联汇编的语法，在编译时将指定的寄存器和值插入到相应的汇编指令中。
具体而言，它使用了csrw汇编指令，将一个32位的值写入到指定的CSR中。reg参数是CSR的名称，val参数是要写入的值。
*/
#define write_csr(reg, val) ({ \
  asm volatile ("csrw " #reg ", %0" :: "rK"(val)); })

请回答如下问题：

在本实验的执行过程中，创建且运行了几个内核线程？