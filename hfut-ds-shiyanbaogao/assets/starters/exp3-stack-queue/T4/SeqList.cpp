#include "SeqList.h"

// 初始化
SeqList::SeqList() {
    count = 0;
}

// 求长度
int SeqList::Length() const {
    return count;
}

// 按序号取元素
error_code SeqList::Get_element(int i, elemenType &x) const {
    if (i < 1 || i > count) {
        return range_error;
    }
    x = data[i - 1];
    return success;
}

// 按值查找，返回序号（从1开始），不存在返回0
int SeqList::Locate(elemenType x) const {
    for (int i = 0; i < count; i++) {
        if (data[i] == x) {
            return i + 1;
        }
    }
    return 0;
}

// 插入元素到第i个位置
error_code SeqList::Insert(int i, elemenType x) {
    if (count == maxLen) {
        return overflow;          // 表满
    }
    if (i < 1 || i > count + 1) {
        return range_error;       // 插入位置非法
    }
    // 从最后一个元素开始向后移动
    for (int j = count; j >= i; j--) {
        data[j] = data[j - 1];
    }
    data[i - 1] = x;
    count++;
    return success;
}

// 删除第i个元素
error_code SeqList::Delete_element(int i) {
    if (count == 0) {
        return underflow;         // 空表
    }
    if (i < 1 || i > count) {
        return range_error;       // 删除位置非法
    }
    // 将后面的元素前移
    for (int j = i; j < count; j++) {
        data[j - 1] = data[j];
    }
    count--;
    return success;
}

/*以上内容为基础数据结构实现*/
/*<STUDENT_IMPLEMENTATION_BEGIN>*/
/*<STUDENT_IMPLEMENTATION_END>*/
