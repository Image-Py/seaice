海冰影像分析软件操作手册
======================

![](http://idoc.imagepy.org/ice//logo.png "")
## Modis 影像分割
----------------
### 打开影像
这里不要使用软件默认的打开方式，请使用 **Ice > Geo TIF Open** 进行导入，这样能保证读取时同时得到TIF的投影信息。 
![](http://idoc.imagepy.org/ice//modis1.jpg "")

### 框选感兴趣区域
用矩形工具框选冰取，然后 **Ice > Duplicate With Projection**
![](http://idoc.imagepy.org/ice//modis2.jpg "")

### 导入海岸线数据，并用Grabcut工具分割
1. **Ice > Land Edge** 导入海岸线
2. **Edit > Clear Out** 清除背景
3. 选择grabcut工具，在图像上标记前景（左键，红色），背景（右键，蓝色）
4. 按住*ctrl*键，单机左键，得到冰缘线
5. 如果不满意，可以继续用左键，右键修补标记，然后*ctrl+z*进行撤销，然后再次按住*ctrl*键，单机左键，直到效果满意。
6. 最后一次撤销后，按住*alt*键，单机左键，得到分割结果

*以上操作也可使用右键，不同的是程序使用分水岭进行分割*

![](http://idoc.imagepy.org/ice//modis3.jpg "")

### 转灰度，增强
**Image > Type > 8-bit** 将图像转为8为灰度，**Process > Filter > Unsharp Mask** 锐化增强
![](http://idoc.imagepy.org/ice//modis4.jpg "")

### 阈值化，打碎
**Image > Adjust > Threshold** 阈值化处理， **Process > Binary > Binary Watershed** 打碎
![](http://idoc.imagepy.org/ice//modis5.jpg "")

### 叠加效果展示
![](http://idoc.imagepy.org/ice//modis.gif "")

## 高分辨率影像分割
------------------
### 打开图像，进行梯度提取
1. **File > Open** 打开图像
2. **Process > Filter > Sobel** 梯度计算
3. **Process > Math > Multiply** 根据情况可以适当对图像进行乘法，提高亮度
4. **Process > Filter > Gaussian** 对图像进行一定程度的平滑（这个可以防止过度分割）

![](http://idoc.imagepy.org/ice//hd1.jpg "")

### 求局部极值点，对梯度图做分水岭分割
1. **Process > Hydrology > Find Minimum* 求局部最小值点
2. **Process > Hydrology > Watershed With ROI** 用最小值点当作种子，对梯度图做分水岭分割

![](http://idoc.imagepy.org/ice//hd2.jpg "")

### 密度分析
用 **Analysis > Region Analysis > Intensity Filter** 结合掩模与原图，用密度分析，识别每个块是冰还是水
![](http://idoc.imagepy.org/ice//hd3.jpg "")

### 叠加效果展示
![](http://idoc.imagepy.org/ice//hd.gif "")

## 雷达影像运动检测
------------------
### 导入雷达影像
**File > Import > Import Sequence** 导入雷达影像序列
![](http://idoc.imagepy.org/ice//move.jpg "")

### 运动分析
**Ice > Moveing Detect** 运动分析
![](http://idoc.imagepy.org/ice//move.gif "")

## 更多功能
----------
软件使用 ImagePy 开源框架为底层，在此基础上，进行了一系列扩展开发，ImagePy 包含了丰富的图像处理功能，对滤波，增强，分割，测量都有很好的支持，并且是一个扩展性很强的开源框架，更多功能可以就在官网获得技术支持。
![](http://idoc.imagepy.org/ice//view.jpg "")