#ifndef LINKLIST_H
#define LINKLIST_H

// 定义元素类型
typedef int elemenType;

// 定义错误码枚举
enum error_code {
    success,        // 操作成功
    overflow,       // 表满溢出（动态链表一般不会满，保留）
    underflow,      // 表空下溢
    range_error,    // 序号越界
    error           //程序错误 
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
    LinkList();                     // 构造函数，创建头结点
    ~LinkList();                    // 析构函数，释放所有结点
    int Length() const;             // 求表长
    error_code Get_element(int i, elemenType &x) const;  // 按序号取元素
    Node* Locate(elemenType x) const;                     // 按值查找，返回结点指针，NULL表示不存在
    error_code Insert(int i, elemenType x);               // 在第i个位置插入元素
    error_code Delete_element(int i);                     // 删除第i个元素

    // 构造链表（扩展功能，可选）
    void CreateFromHead();          // 头插法建立链表（输入以结束符终止）
    void CreateFromTail();          // 尾插法建立链表（输入以结束符终止）
/*<STUDENT_DECLARATIONS_BEGIN>*/
/*<STUDENT_DECLARATIONS_END>*/

};

#endif
