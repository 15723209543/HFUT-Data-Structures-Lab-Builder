#ifndef CREATE_BI_TREE_H
#define CREATE_BI_TREE_H

#include <iostream>
#include <cstdio>
#include <cstring>
using namespace std;

#define NODENUM  100       //定义最大结点数

typedef char elementType;

//二叉树的二叉链表结点结构，也就是二叉树的指针存储结构
typedef struct btNode {
	elementType data;            //结点数据域
	struct btNode *lChild;       //左孩子指针
	struct btNode *rChild;       //右孩子指针
} btNode,*biTree;

//二叉树类：包含二叉链表根指针和创建、遍历算法
class BiTreeClass {
	public:
		btNode *root;        //二叉树指针存储结构的根指针
		void strLTrim(char* str);  //申明删除字符串左边空格
		//层次遍历--因为结构定义及运算实现的次序关系，临时放在此处
		void hieTraverse(btNode *T);
		//键盘交互创建二叉树开始-------------------------------------------------------------------------
		//键盘交互递归创建二叉树子树函数
		void createSubTree(btNode *&p, int k);
		//键盘交互创建二叉树主控函数
		void createBTConsole(btNode *&T);
		//键盘交互创建二叉树开始-------------------------------------------------------------------------
		//键盘交互完全二叉树方式创建二叉树结束-------------------------------------------------------------------------
		void getCompleteArr(elementType *arr, int &num);
		void createBtArr(btNode* &T, elementType* InArr, int i, int n);
		//键盘交互完全二叉树方式创建二叉树结束-------------------------------------------------------------------------
		//数据文件创建二叉树开始-------------------------------------------------------------------------
		//********************** 从数据文件创建二叉树 ***********************//
		//* 分两步完成：第一步将数据从文本文件读入数组                      *//
		//* 第二步从数组递归创建二叉树                                      *//
		//* 两步由2个函数完成                                               *//
		//*******************************************************************//
		//从文本文件数据读入到数组中，同时返回实际结点数量
		bool ReadFileToArray(char fileName[], char strLine[NODENUM][3], int & nArrLen);
		//从数组创建二叉树--数组中保存的是二叉树的先序序列，及每个结点的子树信息
		bool CreateBiTreeFromFile(btNode* & pBT, char strLine[NODENUM][3],int nLen, int & nRow);
		//数据文件创建二叉树结束------------------------------------------------------------------------
				
		/*以上内容复制的是老师文件*/
		/*以下内容为我自己实现*/
/*<STUDENT_DECLARATIONS_BEGIN>*/
/*<STUDENT_DECLARATIONS_END>*/
};

#endif
