#coding:utf-8
import random
import os
from itertools import product
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

"""
基本：
1 图片size
2 字符个数
3 字符区域（重叠、等分）
4 字符位置（固定、随机）
5 字符size（所占区域大小的百分比）
6 字符fonts
7 字符 type （数字、字母、汉字、数学符号）
8 字符颜色
9 背景颜色

高级：
10 字符旋转
11 字符扭曲
12 噪音（点、线段、圈）
"""
chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabdefghijlmnqrtuwxy"

def decode(y):
    y = np.argmax(np.array(y), axis=2)[:,0]
    return ''.join([chars[x] for x in y])

#----------------------------------------------------------------------
def sin(x, height):
    """"""
    a = float(random.choice([5, 12, 24, 48, 128]))
    d = random.choice([2, 4])
    c = random.randint(1, 100)
    b = 2 * random.random()
    return np.array(map(int, height / d * (np.sin((x+c)/a) + b)))

def randRGB():
    return (random.randint(50, 100), random.randint(50, 100), random.randint(50, 100))

def cha_draw(cha, text_color, font, rotate,size_cha):
    im = Image.new(mode='RGBA', size=(size_cha*2, size_cha*2))
    drawer = ImageDraw.Draw(im) 
    drawer.text(xy=(-1, -1), text=cha, fill=text_color, font=font) #text 内容，fill 颜色， font 字体（包括大小）
    drawer.text(xy=(1, -1), text=cha, fill=text_color, font=font)
    drawer.text(xy=(-1, -1), text=cha, fill=text_color, font=font)
    drawer.text(xy=(-1, 1), text=cha, fill=text_color, font=font)
    drawer.text(xy=(-1, 0), text=cha, fill=text_color, font=font)
    drawer.text(xy=(1, 0), text=cha, fill=text_color, font=font)
    drawer.text(xy=(0, -1), text=cha, fill=text_color, font=font)
    drawer.text(xy=(0, 1), text=cha, fill=text_color, font=font)
    drawer.text(xy=(0, 0), text=cha, fill=(255, 255, 255), font=font)
    if rotate:
        max_angle = 20 # to be tuned
        angle = random.randint(-max_angle, max_angle)
        im = im.rotate(angle, Image.BILINEAR, expand=1)
    im = im.crop(im.getbbox())
    return im

def captcha_draw(size_im, nb_cha, set_cha, fonts=None, overlap=0.1, 
        rd_bg_color=False, rd_text_color=False, rd_text_pos=False, rd_text_size=False,
        rotate=False, noise=None, dir_path=''):
    """
        overlap: 字符之间区域可重叠百分比, 重叠效果和图片宽度字符宽度有关
        字体大小 目前长宽认为一致！！！
        所有字大小一致
        扭曲暂未实现
        noise 可选：point, line , circle
        fonts 中分中文和英文字体
        label全保存在label.txt 中，文件第i行对应"i.jpg"的图片标签，i从1开始
    """
    rate_cha = 1.3 # rate to be tuned
    width_im, height_im = size_im
    width_cha = int(width_im / max(nb_cha-overlap, 1)) # 字符区域宽度
    height_cha = height_im # 字符区域高度
    bg_color = 'white'
    text_color = random.choice([(254, 101, 101), (101, 101, 254)])

    if rd_text_size:
        rate_cha = random.uniform(rate_cha-0.1, rate_cha+0.1) # to be tuned
    size_cha = int(rate_cha*min(width_cha, height_cha)) # 字符大小
    
    #if rd_bg_color:
        #bg_color = randRGB()
    bg_color = (255, 255, 255)
    im = Image.new(mode='RGB', size=size_im, color=bg_color) # color 背景颜色，size 图片大小

    drawer = ImageDraw.Draw(im)
    contents = []
    derx = random.randint(0, max(width_cha-size_cha-5, 0))
    dery = 0
    for i in range(nb_cha):
        if rd_text_pos:
            #derx += random.randint(0, max(width_cha-size_cha-5, 0))
            dery = random.randint(0, max(height_cha-size_cha-5, 0))

        # font = ImageFont.truetype("arial.ttf", size_cha)
        cha = random.choice(set_cha)
        font = ImageFont.truetype(fonts['eng'], size_cha)
        contents.append(cha) 
        char_size = int((0.01 * random.randint(0, 20) + 1) * size_cha)
        im_cha = cha_draw(cha, text_color, font, rotate, char_size)
        derx += random.randint(0, 5)
        im.paste(im_cha, 
                 (derx, dery++random.randint(0, 5)), 
                 im_cha) # 字符左上角位置
        derx += size_cha / 2
        
    if 'point' in noise:
        nb_point = 30
        color_point = randRGB()
        for i in range(nb_point):
            x = random.randint(0, width_im)
            y = random.randint(0, height_im)
            drawer.point(xy=(x, y), fill=color_point)
    if 'sin' in noise:
        img = np.asarray(im)
        x = np.arange(0, width_im)
        y = sin(x, height_im)
        for k in range(4):
            for i, j in zip(x, y+k):
                drawer.point(xy=(i, j), fill=text_color)
    if 'line' in noise:
        nb_line = 10
        for i in range(nb_line):
            color_line = randRGB()
            sx = random.randint(0, width_im)
            sy = random.randint(0, height_im)
            ex = random.randint(0, width_im)
            ey = random.randint(0, height_im)
            drawer.line(xy=(sx, sy, ex, ey), fill=color_line)
    if 'circle' in noise:
        nb_circle = 5
        color_circle = randRGB()
        for i in range(nb_circle):
            sx = random.randint(0, width_im-50)
            sy = random.randint(0, height_im-20)
            ex = sx+random.randint(15, 25)
            ey = sy+random.randint(10, 15)
            drawer.arc((sx, sy, ex, ey), 0, 360, fill=color_circle)
            
    return np.asarray(im), contents

def captcha_generator(width, 
                      height, 
                      batch_size=64,
                      set_cha=chars
                      ):
    size_im = (width, height)
    rd_text_poss = [True, True]
    rd_text_sizes = [True, True]
    rd_text_colors = [True, True] # false 代表字体颜色全一致，但都是黑色
    rd_bg_color = True 
    noises = [['sin']]
    rotates = [True, True]
    font_dir = 'fonts/english'
    font_paths = []
    for dirpath, dirnames, filenames in os.walk(font_dir):
        for filename in filenames:
            filepath = dirpath + os.sep + filename
            font_paths.append({'eng':filepath})
            
    n_len = 5
    n_class = len(set_cha)
    X = np.zeros((batch_size, height, width, 3), dtype=np.uint8)
    y = [np.zeros((batch_size, n_class), dtype=np.uint8) for i in range(n_len)]    
    while True:
        for i in range(batch_size):
            overlap = 0
            rd_text_pos = random.choice(rd_text_poss)
            rd_text_size = random.choice(rd_text_sizes)
            rd_text_color = random.choice(rd_text_colors)
            noise = random.choice(noises)
            rotate = random.choice(rotates)
            nb_cha = 5
            font_path = random.choice(font_paths)
            dir_name = 'all'
            dir_path = 'img_data/'+dir_name+'/'
            im, contents = captcha_draw(size_im=size_im, nb_cha=nb_cha, set_cha=set_cha, 
                                        overlap=overlap, rd_text_pos=rd_text_pos, rd_text_size=False, 
                                        rd_text_color=rd_text_color, rd_bg_color=rd_bg_color, noise=noise, 
                                        rotate=rotate, dir_path=dir_path, fonts=font_path)
            contents = ''.join(contents)
            X[i] = im
            for j, ch in enumerate(contents):
                y[j][i, :] = 0
                y[j][i, set_cha.find(ch)] = 1
        yield X, y
        
#----------------------------------------------------------------------
def captcha_save():
    """"""
    a = captcha_generator(100, 40)
    dir_path = 'img_data/all/'
    X, y = a.next()
    for x in X:
        if os.path.exists(dir_path) == False: # 如果文件夹不存在，则创建对应的文件夹
            os.makedirs(dir_path)
            pic_id = 1
        else:
            pic_names = map(lambda x: x.split('.')[0], os.listdir(dir_path))
            #pic_names.remove('label')
            pic_id = max(map(int, pic_names))+1 # 找到所有图片的最大标号，方便命名
    
        img_name = str(pic_id) + '.jpg'
        img_path = dir_path + img_name
        label_path = dir_path + 'label.txt'
        #with open(label_path, 'a') as f:
            #f.write(''.join(pic_id)+'\n') # 在label文件末尾添加新图片的text内容
        print img_path
        img = Image.fromarray(np.uint8(x))
        img.save(img_path)            

if __name__ == "__main__":
    for _ in range(100):
        captcha_save()
