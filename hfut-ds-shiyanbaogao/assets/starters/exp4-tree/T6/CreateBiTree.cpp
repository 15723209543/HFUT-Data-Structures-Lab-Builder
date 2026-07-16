#include "CreateBiTree.h"

//层次遍历--因为结构定义及运算实现的次序关系，临时放在此处
void BiTreeClass::hieTraverse(btNode *T) {
	btNode *queue[NODENUM];
	btNode *p;
	int front;
	int rear;
	if(T==NULL)
		return;
	front=0;
	rear=0;
	queue[rear]=T;
	rear=(rear+1)%NODENUM;
	while(front!=rear) {
		p=queue[front];
		front=(front+1)%NODENUM;
		cout<<p->data<<" ";         //访问根结点。打印当前结点元素值，替代visit(T)函数
		if(p->lChild) {
			queue[rear]=p->lChild;
			rear=(rear+1)%NODENUM;
		}
		if(p->rChild) {
			queue[rear]=p->rChild;
			rear=(rear+1)%NODENUM;
		}
	}
	cout<<endl;
}

//键盘交互创建二叉树开始-------------------------------------------------------------------------
//键盘交互递归创建二叉树子树函数
void BiTreeClass::createSubTree(btNode *&p, int k) {
	//k=1--左子树；k=2--右子树
	btNode *s;
	elementType x;
	cout<<"请输入结点元素数值，'/'表示无子树，x=";
	cin>>x;
	if(x!='/') {
		s=new btNode;
		s->data=x;
		s->lChild=NULL;
		s->rChild=NULL;
		if(k==1)
			p->lChild=s;     //s接到p的左孩子
		if(k==2)
			p->rChild=s;     //s接为p的右孩子
		createSubTree(s,1);  //递归创建s的左子树
		createSubTree(s,2);  //递归创建s的右子树
	}
}

//键盘交互创建二叉树主控函数
void BiTreeClass::createBTConsole(btNode *&T) {
	btNode *p;
	elementType x;
	p=NULL;
	cout<<"请按先序序列输入二叉树结点，（‘/’表示无子树）:"<<endl;
	cout<<"请输入结点元素数值，'/'表示无子树，x=";
	cin>>x;
	if(x=='/') {
		T=NULL;
		return;    //空树，退出
	}
	T=new btNode;
	T->data=x;
	T->lChild=NULL;
	T->rChild=NULL;
	p=T;
	(void)p;

	createSubTree(T,1);    //创建根结点的左子树
	createSubTree(T,2);    //创建根结点的右子树
}
//键盘交互创建二叉树开始-------------------------------------------------------------------------

//键盘交互完全二叉树方式创建二叉树开始-------------------------------------------------------------------------
void BiTreeClass::getCompleteArr(elementType *arr, int &num) {
	//完全二叉树顺序存储方式创建二叉链表结构二叉树
	//缺少的结点数值用'/'代替
	//用'#'结束结点输入
	//arr为结点数组
	//num返回实际结点数
	elementType x;
	int i=1;   //arr[0]单元不用
	num=0;
	cout<<"请按完全二叉树方式输入二叉树结点，‘/’表示缺少结点，'#'结束输入。"<<endl;
	cout<<"请输入结点元素数值，'/'表示缺少结点，'#'结束输入，x=";
	cin>>x;
	while(x!='#' && i<NODENUM) {
		*(arr+i)=x;
		i++;
		num++;

		cin>>x;
	}
}

void BiTreeClass::createBtArr(btNode* &T, elementType* InArr, int i, int n) {
	//T--为根结点指针
	//InArr--为按完全二叉树存储的树的结点数组
	//i--当前结点序号
	//n--二叉树结点总数
	if(i>n) {
		T=NULL;
		return;
	}
	if(InArr[i]!='/') {     //有效数据创建结点
		T=new btNode;       //创建根结点
		T->data=InArr[i];   //结点赋值
		T->lChild=NULL;
		T->rChild=NULL;
	} else {
		T=NULL;
		return;
	}
	createBtArr(T->lChild, InArr, 2*i, n);    //递归创建T的左子树
	createBtArr(T->rChild, InArr, 2*i+1, n);  //递归创建T的右子树
}

//键盘交互完全二叉树方式创建二叉树结束-------------------------------------------------------------------------


//数据文件创建二叉树开始-------------------------------------------------------------------------
//********************** 从数据文件创建二叉树 ***********************//
//* 分两步完成：第一步将数据从文本文件读入数组                      *//
//* 第二步从数组递归创建二叉树                                      *//
//* 两步由2个函数完成                                               *//
//*******************************************************************//

//从文本文件数据读入到数组中，同时返回实际结点数量
bool BiTreeClass::ReadFileToArray(char fileName[], char strLine[NODENUM][3], int & nArrLen) {
	//读文本文件数据到数组，返回数组及其长度
	FILE* pFile;      //定义二叉树的文件指针
	char str[1000];   //存放读出一行文本的字符串
	char strTemp[10]; //判断是否注释行

	pFile=fopen(fileName,"r");
	if(!pFile) {
		cout<<"错误：文件"<<fileName<<"打开失败。"<<endl;
		return false;
	}

	while(fgets(str,1000,pFile)!=NULL) { //跳过空行和注释行
		//删除字符串左边空格
		strLTrim(str);
		if (str[0]=='\n')               //空行，继续读取下一行
			continue;

		strncpy(strTemp,str,2);
		strTemp[2]='\0';
		if(strstr(strTemp,"//")!=NULL)  //跳过注释行
			continue;
		else                            //非注释行、非空行，跳出循环
			break;
	}
	//循环结束，str中应该已经是二叉树数据标识"BinaryTree"，判断文件格式
	if(strstr(str,"BinaryTree")==NULL) {
		printf("错误：打开的文件格式错误！\n");
		fclose(pFile);           //关闭文件
		return false;
	}



	//nArrLen=0;
	//while(fscanf(pFile,"%c  %c  %c\n",&strLine[nArrLen][0],&strLine[nArrLen][1],&strLine[nArrLen][2])!=EOF)
	//{
	//printf("%c\n",strLine[nArrLen][0]);
	//	nArrLen++;
	//}

	nArrLen=0;     //数组行号初始化为0
	while(fgets(str,1000,pFile)!=NULL) {
		//删除字符串左边空格
		strLTrim(str);
		if (str[0]=='\n')  //空行，继续读取下一行
			continue;

		strncpy(strTemp,str,2);
		strTemp[2]='\0';
		if(strstr(strTemp,"//")!=NULL)  //注释行，跳过，继续读取下一行
			continue;

		char* token=strtok(str," \t\r\n");   //以空格为分隔符，分割一行数据
		if(token==NULL) { //分割为空串，失败退出
			printf("错误：读取二叉树结点数据失败！\n");
			fclose(pFile); //关闭文件
			return false;
		}

		strLine[nArrLen][0]=*token;  //获取结点数据
		token = strtok( NULL, " \t\r\n");  //读取下一个子串，即此结点的左子树信息
		if(token==NULL) { //分割为空串，失败退出
			printf("错误：读取二叉树结点数据失败！\n");
			fclose(pFile); //关闭文件
			return false;
		}
		strLine[nArrLen][1]=*token;  //获取此结点的左子树信息数据
		token = strtok( NULL, " \t\r\n");  //读取下一个子串，即此结点的右子树信息
		if(token==NULL) { //分割为空串，失败退出
			printf("错误：读取二叉树结点数据失败！\n");
			fclose(pFile); //关闭文件
			return false;
		}
		strLine[nArrLen][2]=*token;  //获取此结点的右子树信息数据

		nArrLen++;  //数组行号加1
		if(nArrLen>=NODENUM)
			break;
	}

	fclose(pFile); //关闭文件
	return true;
}


//从数组创建二叉树--数组中保存的是二叉树的先序序列，及每个结点的子树信息
bool BiTreeClass::CreateBiTreeFromFile(btNode* & pBT, char strLine[NODENUM][3],int nLen, int & nRow) {
	//strLine[NODENUM][3]--保存节点数据的二维数组
	//nLen--数组长度，即：节点个数
	//nRow--数组当前行号

	if((nRow>=nLen) || (nLen==0))
		return false;  //数据已经处理完毕，或者没有数据，退出

	//根据数组数据递归创建子树
	pBT=new btNode;
	pBT->data=strLine[nRow][0];
	pBT->lChild=NULL;
	pBT->rChild=NULL;

	int nRowNext=nRow;  //保留本次递归的行号

	if(strLine[nRowNext][1]=='1') { //当前结点有左子树，递归创建左子树，读下一行数据
		nRow++;
		CreateBiTreeFromFile(pBT->lChild, strLine,nLen,nRow);
	}

	if(strLine[nRowNext][2]=='1') { //当前结点有右子树，递归创建右子树，读下一行数组
		nRow++;
		CreateBiTreeFromFile(pBT->rChild, strLine,nLen,nRow);
	}

	return true;
}


//数据文件创建二叉树结束------------------------------------------------------------------------



//删除字符串、字符数组左边空格
void BiTreeClass::strLTrim(char* str) {
	int i,j;
	int n=0;
	n=strlen(str)+1;
	for(i=0; i<n; i++) {
		if(str[i]!=' ')  //找到左起第一个非空格位置
			break;
	}
	//以第一个非空格字符为手字符移动字符串
	for(j=0; j<n; j++) {
		str[j]=str[i];
		i++;
	}
}

/*以上内容复制的是老师文件*/
/*以下内容为我自己实现*/
/*<STUDENT_IMPLEMENTATION_BEGIN>*/
/*<STUDENT_IMPLEMENTATION_END>*/
