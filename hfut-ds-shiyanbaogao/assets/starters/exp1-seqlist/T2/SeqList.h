#ifndef SEQLIST_H
#define SEQLIST_H

// 定义元素类型
typedef int elemenType;

// 定义错误码枚举
enum error_code {
    success,        // 操作成功
    fail,           //程序运行错误 
    overflow,       // 表满溢出
    underflow,      // 表空下溢
    range_error     // 序号越界
};

const int maxLen = 100;   // 顺序表最大容量

class SeqList {
public:
	//顺序线性表正常定义（开始） 
    SeqList();                          // 构造函数，初始化空表
    int Length() const;                 // 求表长
    error_code Get_element(int i, elemenType &x) const;  // 按序号取元素
    int Locate(elemenType x) const;     // 按值查找，返回序号（从1开始），0表示不存在
    error_code Insert(int i, elemenType x);   // 插入元素到第i个位置
    error_code Delete_element(int i);         // 删除第i个元素
    void print();                             //打印表格 
    //顺序线性表正常定义（结束） 
    
    //题目要求
/*<STUDENT_DECLARATIONS_BEGIN>*/
/*<STUDENT_DECLARATIONS_END>*/
private:
    elemenType data[maxLen];
    int count;      // 当前元素个数
};

#endif
