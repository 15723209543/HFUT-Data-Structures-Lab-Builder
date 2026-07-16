#include "LinkList.h"
#include <iostream>
using namespace std;

/*链表正常定义（开始）*/ 
// 构造函数：创建头结点
LinkList::LinkList() {
    head = new Node;
    head->next = NULL;
    count = 0;
}

// 析构函数：释放所有结点（包括头结点）
LinkList::~LinkList() {
    Node* p = head;
    while (p != NULL) {
        Node* q = p;
        p = p->next;
        delete q;
    }
}

// 求长度
int LinkList::Length() const {
    return count;   // 或者遍历链表返回结点数，这里直接返回count
}

// 按序号取元素（i从1开始）
error_code LinkList::Get_element(int i, elemenType &x) const {
    if (i < 1 || i > count) {
        return range_error;
    }
    Node* p = head->next;
    int j = 1;
    while (p != NULL && j < i) {
        p = p->next;
        j++;
    }
    if (p == NULL) {
        return range_error;   // 理论上不会发生，因为已检查范围
    }
    x = p->data;
    return success;
}

// 按值查找，返回结点指针
LinkList::Node* LinkList::Locate(elemenType x) const {
    Node* p = head->next;
    while (p != NULL) {
        if (p->data == x) {
            return p;
        }
        p = p->next;
    }
    return NULL;
}

// 在第i个位置插入元素（i从1开始，i=count+1表示表尾插入）
error_code LinkList::Insert(int i, elemenType x) {
    if (i < 1 || i > count + 1) {
        return range_error;
    }
    // 找到第i-1个结点（即插入位置的前驱）
    Node* p = head;
    int j = 0;
    while (p != NULL && j < i - 1) {
        p = p->next;
        j++;
    }
    if (p == NULL) {
        return range_error;   // 理论上不会
    }
    Node* s = new Node;
    s->data = x;
    s->next = p->next;
    p->next = s;
    count++;
    return success;
}

// 删除第i个元素
error_code LinkList::Delete_element(int i) {
    if (i < 1 || i > count) {
        return range_error;
    }
    // 找到第i-1个结点
    Node* p = head;
    int j = 0;
    while (p != NULL && j < i - 1) {
        p = p->next;
        j++;
    }
    if (p == NULL || p->next == NULL) {
        return range_error;
    }
    Node* u = p->next;          // 待删除结点
    p->next = u->next;
    delete u;
    count--;
    return success;
}

// 头插法建立链表（输入以结束符终止，例如输入-1结束）
void LinkList::CreateFromHead() {
    elemenType x;
    cin >> x;
    while (x != -1) {   // 假设-1为结束符，可根据需要修改
        Node* s = new Node;
        s->data = x;
        s->next = head->next;
        head->next = s;
        count++;
        cin >> x;
    }
}

// 尾插法建立链表
void LinkList::CreateFromTail() {
    elemenType x;
    cin >> x;
    Node* rear = head;   // 尾指针
    while (x != -1) {
        Node* s = new Node;
        s->data = x;
        s->next = NULL;
        rear->next = s;
        rear = s;
        count++;
        cin >> x;
    }
}

//打印函数 
void LinkList::print() {
    Node *p = head->next;   
    if (p == NULL) {
        cout << "空表" << endl;
    } else {
        while (p != NULL) {
            cout << p->data << " ";
            p = p->next;
        }
        cout << endl;
    }
}
/*链表正常定义（结束）*/ 

/*题目要求实现*/
/*<STUDENT_IMPLEMENTATION_BEGIN>*/
/*<STUDENT_IMPLEMENTATION_END>*/
