#ifndef LINKLIST_H
#define LINKLIST_H

// 定义元素类型
typedef int elemenType;

// 定义错误码枚举
enum error_code {
    success,        // 操作成功
    fail,           //其他失败 
    underflow,      // 表空下溢
    range_error     // 序号越界
};

class LinkList {
private:
    // 结点结构
    struct Node {
        elemenType data;
        Node* next;
    };

    Node* head;     // 头指针，指向头结点
    int count;      // 元素个数

public:
	/*链表正常定义（开始）*/ 
    LinkList();                     // 构造函数，创建头结点
    ~LinkList();                    // 析构函数，释放所有结点
    int Length() const;             // 求表长
    error_code Get_element(int i, elemenType &x) const;  // 按序号取元素
    Node* Locate(elemenType x) const;                     // 按值查找，返回结点指针，NULL表示不存在
    error_code Insert(int i, elemenType x);               // 在第i个位置插入元素
    error_code Delete_element(int i);                     // 删除第i个元素
    // 构造链表
    void CreateFromHead();          // 头插法建立链表（输入以结束符-1终止）
    void CreateFromTail();          // 尾插法建立链表（输入以结束符-1终止）
    void print();                   //打印 
    /*链表正常定义（结束）*/ 
    
    /*题目要求实现*/
/*<STUDENT_DECLARATIONS_BEGIN>*/
/*<STUDENT_DECLARATIONS_END>*/
};

#endif
