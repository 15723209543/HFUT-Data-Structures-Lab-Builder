---
name: hfut-ds-shiyanbaogao
description: Complete HFUT-style data-structures laboratory assignments from an attached DOCX requirement file by producing one T1...TX Dev-C++ project per problem, GBK C++ source files with class-based data structures, a copied-and-completed DOCX report, its PDF, a code-grounded oral-viva question-and-answer PDF, and a final ZIP. Preserve teacher starter code, edit only the final algorithm/result/reflection report sections, use text placeholders for screenshots, and prevent privacy leakage or AI-generation labels. Use when the user invokes $hfut-ds-shiyanbaogao, types the compatibility alias $hfut_ds_shiyanbaogao, or asks for 合工大数据结构实验、数据结构实验代码及报告、Dev-C++ 分题工程、实验报告后三部分续写、老师验收模拟提问、实验答辩问答。
---

# HFUT 数据结构实验代码与报告

从实验要求 DOCX 生成可提交的代码、报告、PDF、面对面验收问答 PDF 与 ZIP。把用户材料视为私密数据；只在本次任务输出中保留用户输入里已有且报告本身需要的信息，绝不把姓名、学号、电话、班级、地址、设备路径或文档元数据写回 Skill、README、示例或公共资源。验收问答 PDF 不写身份信息，也不展示源码。

## 开始前

1. 读取 [references/output-contract.md](references/output-contract.md)。
2. 读取 [references/report-schema.md](references/report-schema.md)。
3. 读取 [references/viva-guide.md](references/viva-guide.md)。
4. 当要求匹配五个内置实验之一时，再读取 [references/starter-profiles.md](references/starter-profiles.md)。
5. 记录要求 DOCX 的绝对路径与 SHA-256。不得修改、覆盖或重命名原文件。
6. 同时检查 DOCX 同目录中的教师源文件、测试数据与附件；它们优先于内置 starter。

## 工作流

### 1. 解析要求

运行：

```powershell
python <skill-dir>/scripts/inspect_requirements.py <要求.docx> --output <工作目录>/requirements.json
```

核对实验标题、必做题、扩展题、测试数据、报告三个语义章节、附件和建议 profile。不能只根据章节数字判断：含扩展实验时，后三节可能是 5—7 而不是 4—6。默认完成要求中出现的必做题和扩展题；明确写为无需完成的内容除外。

### 2. 建立输出骨架

运行：

```powershell
python <skill-dir>/scripts/prepare_submission.py <要求.docx> <输出文件夹> --problems <题数> --profile <profile或auto>
```

脚本把要求复制到隐藏工作目录，并在输出根目录建立 `T1` 至 `TX`。不要在 Skill 目录写任务产物。若用户指定输出位置，严格使用该位置；否则优先写到要求文件旁边的独立“完成版”文件夹，附件环境不可写时才使用当前工作区。

### 3. 完成代码

每题只实现本题算法：

- 每个 `TX` 是独立 Dev-C++ 工程，包含恰好一个 `.dev`、`main.cpp`、对应 `.cpp/.h` 和本题测试数据。
- 教师文件或 starter 中“学生实现”标记以前的字节必须保持不变。使用 `patch_gbk.py` 只替换学生声明区和实现区。
- `main.cpp` 只放测试数据、构造对象和调用公开成员函数；不得在其中定义数据结构、成员函数或完成算法主体。
- 所有数据结构与算法入口用类和对象封装。算法声明放 `.h` 的学生区，实现放 `.cpp` 的学生区。
- 关键分支、循环不变量、边界处理和复杂指针变化写简洁中文注释。
- 源码、头文件、Dev-C++ 工程文件及文本测试数据必须能以严格 GBK 解码。先在 UTF-8 临时文件编写，再用 `write_gbk.py` 转码；不得用替换字符掩盖编码错误。
- 测试要求中的全部数据，并补充空结构、单元素、越界/不存在、重复值或不连通等适用边界用例。

用脚本更新 Dev-C++ 工程：

```powershell
python <skill-dir>/scripts/generate_dev_project.py <TX目录> --name TX
```

逐题编译和运行。只执行本次生成、已审阅的代码；设置超时。保留实际输入、输出与结论，供报告第五部分使用。编译器不可用时完成静态检查，并在交付说明中如实说明，不得声称运行通过。

### 4. 生成报告内容

先按 [references/report-schema.md](references/report-schema.md) 写 `report-spec.json`。算法思想必须包含“题目分析 + 做法 + 时间复杂度 + 空间复杂度”，每题不超过 150 字；步骤使用 `①` 至 `⑩`，最多十步；总结、心得和建议合计超过 800 字，建议不超过 100 字。

运行：

```powershell
python <skill-dir>/scripts/fill_report.py <输出文件夹>/.hfut-ds-work/report-base.docx <report-spec.json> --output <输出文件夹>/<实验名>-实验报告.docx
```

必须保留原 DOCX 的前三个语义部分、表格、页眉页脚和已有私密字段，只替换“算法设计与实现描述”“运行结果截图及说明”“总结、心得和建议”三个语义章节。若原要求明确标注“提交报告时删除附录”，删除该附录。所有新增文字为宋体五号、首行缩进 2 字符、单倍行距；板块编号用 `（1）`，内部小标题用 `【】`。

代码结构、算法代码和运行结果均使用明确的图片文字占位，不伪造截图，例如：

```text
【图片位置：插入 T1/SeqList.h 中共用数据类型定义的完整截图，需包含类名、成员变量和必要注释。】
```

### 5. DOCX、PDF 与可视检查

按照 `documents` Skill 的模板编辑与 render-and-verify 流程检查最终 DOCX 的每一页。再运行：

```powershell
python <skill-dir>/scripts/convert_report.py <报告.docx> --output-pdf <报告.pdf> --render-dir <渲染目录>
```

优先使用 Microsoft Word，其次 LibreOffice。若两者均不可用，不得伪造 PDF；明确报告转换受阻。检查所有页面是否有乱码、截断、重叠、异常分页或图片占位丢失。

### 6. 生成面对面验收问答 PDF

先从本次题目、报告内容和实际代码提取证据：

```powershell
python <skill-dir>/scripts/extract_viva_evidence.py <输出文件夹> --spec <report-spec.json> --requirements <requirements.json> --output <工作目录>/viva-evidence.json
```

按照 [references/viva-guide.md](references/viva-guide.md) 和 `assets/viva-spec.example.json` 在 `<输出文件夹>/.hfut-ds-work/` 中写 `viva-spec.json`。逐题核对真实类名、成员函数、数据结构、运行链路、复杂度、测试结果和边界处理；不得只从通用题库复制答案。每题准备 8—16 个短问答，共性问题至少 8 个，运行与调试问题至少 6 个。答案使用学生能够自然说出的专业术语，先给结论再简述原因，单个答案不超过 220 字。

运行：

```powershell
python <skill-dir>/scripts/generate_viva_guide.py --spec <viva-spec.json> --evidence <viva-evidence.json> --output <输出文件夹>/<实验名>-验收问答.pdf --render-dir <渲染目录>
```

问答 PDF 必须能脱离源码用于口述复习，但不能臆造代码没有使用的实现。内容覆盖题目目标、结构选择、类封装、核心不变式、算法步骤、循环/递归/指针运行过程、时间与空间复杂度、边界情况、测试验证、常见错误和替代方案。按照 `pdf` Skill 逐页检查；不得交付乱码、裁切、重叠、空白页或身份信息。

### 7. 校验与打包

运行：

```powershell
python <skill-dir>/scripts/validate_submission.py <输出文件夹> --problems <题数> --spec <report-spec.json> --viva-spec <viva-spec.json>
python <skill-dir>/scripts/package_submission.py <输出文件夹> --output <实验名>-完成版.zip
```

修复全部 `ERROR` 后再交付。校验必须覆盖：连续 `T1...TX`、Dev-C++ 工程引用、GBK、教师前缀、类封装、`main.cpp` 边界、报告字数与格式、截图占位、报告 PDF 与验收问答 PDF、问答题数和隐私、无乱码和无来源生成标记。最终 ZIP 不得包含 `.hfut-ds-work`、缓存、临时 JSON、渲染图、编译产物、个人机器路径或 Skill 自身文件。

## 交付

交付完成版文件夹与 ZIP，简要列出题数、报告 DOCX、报告 PDF、验收问答 PDF、模拟问题总数、编译/运行状态、视觉 QA 状态及任何无法验证项。不要在实验文件名、正文、源码注释、PDF 属性或 ZIP 内写“AI 生成”“ChatGPT”“Codex”等来源字样。
