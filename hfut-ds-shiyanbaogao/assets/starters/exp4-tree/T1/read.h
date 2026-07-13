#ifndef READ_H
#define READ_H

#include "createTree.h"
#include "CreateBiTree.h"

//读取类：专门负责从文件中读取普通树、森林或者二叉树
class read {
	public:
		//读取二叉树
		//fileName：二叉树数据文件名
		//bt：二叉树类对象，用来保存读取后得到的二叉链表二叉树
		void readbt(char fileName[], BiTreeClass &bt);

		//读取普通树或者森林
		//fileName：普通树或者森林数据文件名
		//t：树类对象，用来保存读取后得到的双亲表示和孩子兄弟链表
		void readt(char fileName[], TreeClass &t);
};

#endif
