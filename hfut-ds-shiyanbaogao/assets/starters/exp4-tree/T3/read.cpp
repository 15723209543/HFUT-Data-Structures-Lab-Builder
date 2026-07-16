#include "read.h"
#include <iostream>

using namespace std;

//读取二叉树
//fileName：二叉树数据文件名
//bt：二叉树类对象，用来保存读取后得到的二叉链表二叉树
void read::readbt(char fileName[], BiTreeClass &bt)
{
	char strLine[NODENUM][3];    //保存文件中读取出来的二叉树结点信息
	int nArrLen;                 //实际读取到的结点数量
	int nRow;                    //递归创建二叉树时当前处理到的行号

	nArrLen = 0;
	nRow = 0;
	bt.root = NULL;

	//第一步：从文件中读取二叉树数据到数组
	if(!bt.ReadFileToArray(fileName, strLine, nArrLen))
	{
		cout << "二叉树文件读取失败。" << endl;
		return;
	}

	//第二步：根据数组递归创建二叉链表二叉树
	if(!bt.CreateBiTreeFromFile(bt.root, strLine, nArrLen, nRow))
	{
		cout << "二叉树创建失败。" << endl;
		bt.root = NULL;
		return;
	}

	cout << "二叉树读取成功。" << endl;
}

//读取普通树或者森林
//fileName：普通树或者森林数据文件名
//t：树类对象，用来保存读取后得到的双亲表示和孩子兄弟链表
void read::readt(char fileName[], TreeClass &t)
{
	int ok;    //判断普通树或者森林文件是否读取成功

	//初始化树类对象中的双亲表示和孩子兄弟链表根指针
	t.initialTree(t.parentTree);
	t.csRoot = NULL;
	ok = 0;

	//第一步：从文件中读取普通树或者森林，得到双亲表示结构
	ok = t.CreateTreeFromFile(fileName, t.parentTree);
	if(!ok)
	{
		cout << "普通树或者森林文件读取失败。" << endl;
		t.parentTree.n = 0;
		t.csRoot = NULL;
		return;
	}

	//第二步：由双亲表示结构创建孩子兄弟链表指针存储结构
	//如果文件是普通树，csRoot就是普通树根结点
	//如果文件是森林，csRoot就是森林第一棵树的根结点，后续根结点通过nextSibling连接
	t.createCsTree(t.csRoot, t.parentTree);

	cout << "普通树或者森林读取成功。" << endl;
}
