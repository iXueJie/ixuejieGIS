# ixuejieGIS

个人课程作业，请勿在生产中使用。\
Individual coursework, do **NOT** use in production. 

![](https://images2.alphacoders.com/108/1083411.jpg)

> 作者的一点小爱好:stuck_out_tongue_winking_eye:

## 主要功能

#### 作业要求的功能

- 简单加载矢量、栅格图像

- 放大，缩小，平移，缩放至图层

- 波段运算

- 栅格按矢量掩膜裁剪

- 查看矢量图层的属性

- 符号渲染：简单符号渲染、渐变符号渲染、分类符号渲染
  （分类符号渲染有bug，不要点击分类按钮！不要点击！不要点击！）
  （警告：请不要像此项目中一样使用QgsRendererWidget，正确打开方式参考[官方文档](https://www.qgis.org/pyqgis/3.4/gui/QgsRendererWidget.html)）

  > WORKFLOW: - open renderer dialog with some RENDERER (never null!) - find out which widget to use - instantiate it and set in stacked widget - on any change of renderer type, create some default (dummy?) version and change the stacked widget - when clicked OK/Apply, get the renderer from active widget and clone it for the layer

- 制图，并导出为图片

#### 启动界面

图片可以根据喜好更滑，只需要将图片放入 `res\bg` 路径下即可。

#### 问题 JSON 格式

[点击这里](./doc/puzzle_example.json)查看更多。

~~~json
{
    "name": "Name of your puzzle set",
    "content": [
        {
            "_id": 10001,
            "problem": "Puzzle description?",
            "options": [
                "option_a",
                "option_b",
                "option_c",
                "option_d"
            ],
            "key_idx": 0
        }
    ]
}
~~~

目前已经有5类问题集，分别是

- 动画
- 计算机
- 生活
- 数学-物理
- 游戏
- 专业知识

如果还想添加更多问题，可以按照上述格式在现有的问题集中追加，或者新建你的问题集 json 文件并在代码中使用它。

~~~python
# puzzle_set_example.json

import puzzle

# 可以设置shuffle来打乱选项的顺序。
your_puzzle_set = puzzle.PuzzleSet('puzzle_set_example.json', shuffle=True)
~~~

