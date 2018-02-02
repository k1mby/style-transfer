A tensorflow implementation of style transfer, as outlined in ["A Neural Algorithm of Artistic Style"](https://arxiv.org/pdf/1508.06576.pdf).

Read the [Introduction](intro.html) to learn about the code. See [Setup](setup.html) for installation and usage.

<p align="center">
<img src="src/img/content/grass.jpg" width="300px">  
<img src="src/img/results/select/carmichael.png" width="300px">
</p>

<br>

___
## Requirements

Tensorflow  
Pillow  
Scipy  
numpy  
<br>

___
## References
The original paper "A Neural Algorithm of Artistic Style" [here](https://arxiv.org/pdf/1508.06576.pdf)    
MatConvNet VGG-19 available [here](http://www.vlfeat.org/matconvnet/pretrained/#downloading-the-pre-trained-models)  
The VGG-19 paper [here](https://arxiv.org/pdf/1409.1556.pdf)  
VGG-19 details [here](https://gist.github.com/ksimonyan/3785162f95cd2d5fee77#file-readme-md)

___
## Usage

1. Download the source code

2. Navigate inside the `src` folder of the project

3. Place your style and content images in the `img/style` and `img/content` folders.
Edit the image paths in `style_transfer.py`
```python
STYLE = 'img/style/your_style_image.jpg'
CONTENT = 'img/content/your_content_image.jpg'
```
4. Run the script `style_transfer.py`