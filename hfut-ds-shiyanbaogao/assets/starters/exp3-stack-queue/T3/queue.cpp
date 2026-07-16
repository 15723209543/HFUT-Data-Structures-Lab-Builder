#include "queue.h"

// 构造函数：将队列初始化为空
Queue::Queue() {
    front = 0;
    rear = 0;
    count = 0;
}

// 判断队列是否为空：若 front == rear，则为空
Bool Queue::Empty() const {
    return front == rear;
}

// 判断队列是否为满：采用“保留一个元素空间”的方法，即最多存放 maxlen-1 个元素
Bool Queue::Full() const {
    return count == maxlen - 1;
    // 等价于：return (rear + 1) % maxlen == front;
}

// 取队头元素：若队列非空，将队头元素赋给 x 并返回 success；否则返回 underflow
error_code Queue::Get_front(elemenType &x) const {
    if (Empty()) {
        return underflow;
    }
    // 队头元素位于 front 的下一个位置
    x = data[(front + 1) % maxlen];
    return success;
}

// 入队：若队列未满，将 x 插入队尾，并返回 success；否则返回 overflow
error_code Queue::Append(const elemenType x) {
    if (Full()) {
        return overflow;
    }
    rear = (rear + 1) % maxlen;
    data[rear] = x;
    count++;
    return success;
}

// 出队：若队列非空，删除队头元素，并返回 success；否则返回 underflow
error_code Queue::Serve() {
    if (Empty()) {
        return underflow;
    }
    front = (front + 1) % maxlen;
    count--;
    return success;
}

int Queue::getcount(){
	return count; 
}

/*以上内容为基础数据结构实现*/
/*<STUDENT_IMPLEMENTATION_BEGIN>*/
/*<STUDENT_IMPLEMENTATION_END>*/
