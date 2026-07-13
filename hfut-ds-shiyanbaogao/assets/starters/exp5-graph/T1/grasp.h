#ifndef grasp_h
#define grasp_h

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//图中允许保存的最大顶点个数
const int maxvertexnum = 100;

//无穷大，用在网的邻接矩阵中，表示两个顶点之间没有边或弧
const int INF = 10000;

//顶点元素类型
typedef char elementType;

//邻接矩阵单元类型
//普通图中一般保存 0 或 1；网中保存权值或 INF
typedef int cellType;

//边或弧的附加信息类型
//在网中表示权值，在普通图中一般保存 1
typedef int eInfoType;

//图的类型
//UDG：无向图
//UDN：无向网
//DG ：有向图
//DN ：有向网
enum GraphKind {
    UDG,
    UDN,
    DG,
    DN
};

//边链表结点，用于邻接表存储
struct EdgeNode {
	int adjVer; //邻接点编号，从 1 开始
	eInfoType eInfo;//边或弧的信息，普通图为 1，网为权值
	EdgeNode* next; //指向下一条边或弧
};

//顶点表结点，用于邻接表存储
struct VerNode {
	elementType data;    //顶点元素，例如 a、b、c
	EdgeNode* firstEdge;//指向该顶点第一条边或弧
};

//图的存储结构体
struct Graph {
	elementType Data[maxvertexnum + 1];//邻接矩阵存储时使用的顶点数组
	//邻接矩阵，保存边、弧或权值
	cellType AdjMatrix[maxvertexnum + 1][maxvertexnum + 1];
	VerNode VerList[maxvertexnum + 1];//邻接表顶点数组，每个顶点带一条边链表
	int VerNum;  //顶点个数
	int ArcNum;  //边数或弧数
	GraphKind gKind;    //图的类型
};

//图类
//本类只封装两个参考文件中给出的函数，不额外增加算法函数。
class graph {
	public:
		//删除字符串左边的空格，用于读取文件时跳过行首空格
		void strLTrim(char* str);

		//从边表格式文件创建邻接矩阵表示的图
		//文件中每一行边数据写成：起点 终点 [权值]
		bool CreateGrpFromFile(char fileName[], Graph &G);

		//从邻接矩阵格式文件创建邻接表表示的图
		//文件中边数据部分是一整块矩阵
		int CreateGrpFromFile1(char fileName[], Graph &G);

		//从边表格式文件创建邻接表表示的图
		//文件中每一行边数据写成：起点 终点 [权值]
		int CreateGraphFromFile(char fileName[], Graph &G);

		//销毁邻接表表示的图，释放动态申请的边结点空间
		void DestroyGraph(Graph &G);

		/*以上内容复制的是老师文件*/
		/*以下内容为我自己实现*/
/*<STUDENT_DECLARATIONS_BEGIN>*/
/*<STUDENT_DECLARATIONS_END>*/
};

#endif
