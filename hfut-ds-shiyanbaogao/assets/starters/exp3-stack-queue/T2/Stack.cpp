#include "Stack.h"
#include <iostream>
using namespace std;

/*正常栈定义（开始）*/ 
// 构造函数：将栈初始化为空
Stack::Stack() {
	count = 0;
}

// 判断栈空：若元素个数为0，则返回TRUE，否则返回FALSE
Bool Stack::Empty() const {
	return count == 0;
}

// 判断栈满：若元素个数达到最大容量，则返回TRUE，否则返回FALSE
Bool Stack::Full() const {
	return count == maxlen;
}

// 取栈顶元素：若栈非空，将栈顶元素赋给x并返回success；否则返回underflow
error_code Stack::Get_top(elemenType &x) const {
	if (Empty()) {
		return underflow;
	}
	x = data[count - 1];
	return success;
}

// 入栈：若栈未满，将x压入栈顶并返回success；否则返回overflow
error_code Stack::Push(const elemenType &x) {
	if (Full()) {
		return overflow;
	}
	data[count] = x;
	count++;
	return success;
}

// 出栈：若栈非空，删除栈顶元素并返回success；否则返回underflow
error_code Stack::Pop() {
	if (Empty()) {
		return underflow;
	}
	count--;
	return success;
}

//打印 
void Stack::print(){
	if (Empty()) {
		cout<<"空"<<endl;
	}
	else{
		for(int i=0;i<count;i++){
			cout<<data[i];
		}
		cout<<" ";
	}
}
/*正常栈定义（结束）*/ 

/*以上内容为基础数据结构实现*/
/*<STUDENT_IMPLEMENTATION_BEGIN>*/
/*<STUDENT_IMPLEMENTATION_END>*/
