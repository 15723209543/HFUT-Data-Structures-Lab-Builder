#ifndef STACK_H
#define STACK_H

// 定义元素类型，可根据需要修改为其他类型（如char、double等）
typedef char elemenType;

// 定义Bool类型（此处使用C++的bool）
typedef bool Bool;

// 定义错误码枚举
enum error_code {
    success,    // 操作成功
    overflow,   // 栈满溢出
    underflow,  // 栈空下溢
    fail,       //失败 
    error       //程序错误 
};

// 定义栈的最大容量，可根据实际需求调整
const int maxlen = 100;

// 栈类的定义（顺序存储结构）
class Stack {
	public:
		/*正常栈定义（开始）*/ 
		Stack();                            // 构造函数，初始化空栈
		Bool Empty() const;                 // 判断栈是否为空
		Bool Full() const;                  // 判断栈是否为满
		error_code Get_top(elemenType &x) const; // 取栈顶元素，通过参数返回
		error_code Push(const elemenType &x);     // 入栈（元素x压入栈顶）
		error_code Pop();                    // 出栈（删除栈顶元素）
		void print();                        //打印 
		/*正常栈定义（结束）*/ 

	/*<STUDENT_DECLARATIONS_BEGIN>*/
/*<STUDENT_DECLARATIONS_END>*/

private:
		int count;                          // 栈中当前元素个数
		elemenType data[maxlen];             // 存储栈元素的数组
};

#endif
