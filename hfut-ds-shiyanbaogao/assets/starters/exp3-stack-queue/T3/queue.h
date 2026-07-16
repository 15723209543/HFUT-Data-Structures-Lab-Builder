#ifndef QUEUE_H
#define QUEUE_H

// 定义元素类型，可根据需要修改（如 char、double 等）
typedef int elemenType;

// 定义 Bool 类型（直接使用 C++ 的 bool）
typedef bool Bool;

// 定义错误码枚举
enum error_code {
    success,    // 操作成功
    overflow,   // 队列满溢出
    underflow,  // 队列空下溢
    error       //程序错误 
};

// 定义队列的最大容量（数组大小），实际最多存放 maxlen-1 个元素（保留一个空间）
const int maxlen = 100;

// 队列类的定义（循环队列，顺序存储结构）
class Queue {
public:
    Queue();                            // 构造函数，初始化空队列
    Bool Empty() const;                 // 判断队列是否为空
    Bool Full() const;                  // 判断队列是否为满
    error_code Get_front(elemenType &x) const; // 取队头元素（通过参数返回）
    error_code Append(const elemenType x);     // 入队（将元素 x 插入队尾）
    error_code Serve();                  // 出队（删除队头元素）
    int getcount();                      //确认有多少个元素 

/*<STUDENT_DECLARATIONS_BEGIN>*/
/*<STUDENT_DECLARATIONS_END>*/

private:
    int front, rear;    // 队头前一个位置的下标，队尾元素的下标
    int count;          // 当前队列中的元素个数
    elemenType data[maxlen]; // 存储队列元素的数组
};

#endif
