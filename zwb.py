#coding:utf8
import cv2
from ctypes import *
import numpy as np
import time
import os

#55*55的英雄头像
heroes_55=[]
for i in os.listdir('.\\heroes_thumbnail_55'):
    heroes_55.append((cv2.imread('.\\heroes_thumbnail_55\\'+i,cv2.IMREAD_COLOR),i))

#65*65的英雄头像
heroes_65=[]
for i in os.listdir('.\\heroes_thumbnail_65'):
    heroes_65.append((cv2.imread('.\\heroes_thumbnail_65\\'+i,cv2.IMREAD_COLOR),i))

#匹配英雄
def match_heroes(frame,heroes,flag):
    #背景置为黑色
    if flag:
        radius=(frame.shape[0]-1)//2
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                if (i-radius)**2+(j-radius)**2>radius*radius:
                    frame[i,j]=0
        
    t=[]
    for idx,hero in enumerate(heroes):
        
        res=cv2.matchTemplate(frame,hero[0],cv2.TM_CCOEFF_NORMED)
        res=cv2.minMaxLoc(res)
        t.append((res[1],hero[1]))
    t.sort()
    t=t[::-1]
    return (t[0][1],t[0][0])

#待匹配图片名称和矩形框
all_pic_list=[['blue10.png',[25,62,892,935]],
['red10.png',[25,62,990,1031]],
['shuilong.png',[103,123,124,157]],
['huolong.png',[103,123,124,157]],
['tulong.png',[103,123,124,157]],
['yunlong.png',[103,123,124,157]],
['yuangulong.png',[103,123,124,157]],
['sansha.png',[222,268,900,1017]],
['sisha.png',[222,268,900,1017]],
['wusha.png',[218,272,892,1024]],
['yixue.png',[222,265,868,1052]],
['chaoshen.png',[225,270,851,1240]],
['xiaguxianfeng.png',[226,264,806,1235]],
['diyitiaolong.png',[226,264,852,1210]],
['nashinanjue.png',[226,264,817,1245]],
['yita.png',[226,264,805,1165]]
]

#提示文字的图片名称和矩形框
word_list=[['sansha.png',[222,268,900,1017]],
['sisha.png',[222,268,900,1017]],
['wusha.png',[218,272,892,1024]],
['yixue.png',[222,265,868,1052]],
['chaoshen.png',[225,270,851,1240]],
['xiaguxianfeng.png',[226,264,806,1235]],
['diyitiaolong.png',[226,264,852,1210]],
['nashinanjue.png',[226,264,817,1245]],
['yita.png',[226,264,805,1165]]]

#三杀，四杀，超神的杀人头像和被杀头像和文字的横坐标差值
hero_word_x_diff=[[69,233],[74,239],[],[],[0,208]]

#判断一塔是蓝队拿还是红队拿
yita_list=[['yita_blue.png',None],['yita_red.png',None]]

#所有提示文字的图片名称
wordname_list=list(x[0] for x in word_list)

#带文字提示的图片识别方法：
#取文字的所有像素点和待匹配图片中的文字的所有像素点比较
#占比越大，越匹配
#下面几行代码，保存示例图片的文字所有像素点到c数组里，准备传到c++ dll里计算结果
for i in word_list:
    i.append([])
    temp_pic=cv2.imread('.\\pic_zwb_new\\'+i[0],cv2.IMREAD_COLOR)
    for j in range(temp_pic.shape[0]):
        for k in range(temp_pic.shape[1]):
            if temp_pic[j,k].any():
                i[2].extend([j,k])
    i.append((c_int*len(i[2]))())
    for j in range(len(i[2])):
        i[3][j]=i[2][j]
    i.append(temp_pic.shape)

#处理红队蓝队的文字字样
for i in yita_list:
    i.append([])
    temp_pic=cv2.imread('.\\pic_zwb_new\\'+i[0],cv2.IMREAD_COLOR)
    for j in range(temp_pic.shape[0]):
        for k in range(temp_pic.shape[1]):
            if temp_pic[j,k].any():
                i[2].extend([j,k])
    i.append((c_int*len(i[2]))())
    for j in range(len(i[2])):
        i[3][j]=i[2][j]
    i.append(temp_pic.shape)

word_dic={}
for i in word_list:
    word_dic[i[0]]=i

#dll模块
dll_object = cdll.LoadLibrary('lol.dll')
matchtemplate = dll_object.matchtemplate

#提取所有的文字像素点
def word_extract(frame):
    im=np.zeros(frame.shape[:2]).astype(np.uint8)
    r=abs(frame[:,:,2].astype(np.int)-221)
    g=abs(frame[:,:,1].astype(np.int)-182)
    b=abs(frame[:,:,0].astype(np.int)-148)
    #print(r.shape)
    im[r+g+b<200]=1
    return im

#保存每一帧匹配结果
all_result=[[] for i in range(len(all_pic_list))]
cap = cv2.VideoCapture(r'E:\Downloads\lol_zwb.mp4')

#最终结果
final_result=[None,None,[],[],[],[],[],[],[],[],[]]

#匹配中记录每个文字提示的匹配过程
#[连续匹配的帧数，文字位置的横坐标最小值，文字位置的横坐标最大值，文字位置的纵坐标最小值，文字位置的横坐标最大值，待匹配英雄头像的一帧图片]
temp_list=[[-1,1920,0,1080,0,None] for i in range(9)]



ret,frame = cap.read()
num=1

start=time.clock()
while True:
    ret,frame = cap.read()
    #print(num)
    if num%1000==0:
        print(num,'1000frames: ',time.clock()-start)
        start=time.clock()
    if num<18000:
        num += 1
        continue
    if not ret:
        break
    fim=word_extract(frame[213:277,800:1273])
    for idx,i in enumerate(all_pic_list):
        # 为了避免图像的像素点有偏移
        if i[1][0]<5:
            y1=0
        else:
            y1=i[1][0]-5
        if i[1][2]<5:
            x1=0
        else:
            x1=i[1][2]-5
        if i[1][1]>1075:
            y2=1080
        else:
            y2=i[1][1]+5
        if i[1][3]>1915:
            x2=1920
        else:
            x2=i[1][3]+5
        if not i[0] in wordname_list:
            # 匹配红队，蓝队谁先10杀和第一条龙的信息
            pic=frame[y1:y2,x1:x2]
            pic1=cv2.imread('.\\pic_zwb_new\\'+i[0],cv2.IMREAD_COLOR)
            #print(pic.shape,pic1.shape)
            res=cv2.matchTemplate(pic,pic1,cv2.TM_SQDIFF_NORMED)
            res=cv2.minMaxLoc(res)
            all_result[idx].append((res[0],res[2]))

            if not final_result[0] and res[0]<0.15 and i[0] in ('blue10.png','red10.png'):
                if i[0]=='blue10.png':
                    final_result[0]='blue'
                else:
                    final_result[0]='red'
            if not final_result[1] and res[0]<0.15 and \
                i[0] in ('shuilong.png','huolong.png','tulong.png','yunlong.png','yuangulong.png'):
                final_result[1]=i[0][:i[0].index('.')]
        else:
            y1-=213
            y2-=213
            x1-=800
            x2-=800
            result=(c_float*3)()
            #print(fim.shape,y1,y2,x1,x2)
            im = fim[y1:y2, x1:x2]
            xx1=im.shape[0]
            yy1=im.shape[1]
            im = im.reshape(im.shape[0] * im.shape[1])
            i=word_dic[i[0]]
            s=time.clock()
            #cast(a.ctypes.data, POINTER(c_int)
            matchtemplate(i[3],len(i[2])//2,i[4][0],i[4][1],cast(im.ctypes.data,POINTER(c_int)),xx1,yy1,result)
            #print(i[0],i[4],time.clock()-s,xx1,yy1)
            result=list(result)
            # 文字的位置
            r_x=int(result[2])+800+x1
            r_y=int(result[1])+213+y1

            #print(result)
            all_result[idx].append((1-result[0],(r_x,r_y,np.average(im))))
            # 匹配上文字提示
            if 1-result[0]<0.2:
                #print(r_x, r_y)
                # 上一帧也匹配上
                if temp_list[idx-7][0]!=-1:
                    if r_x<temp_list[idx-7][1]:
                        temp_list[idx-7][1]=r_x
                    if r_x>temp_list[idx-7][2]:
                        temp_list[idx-7][2]=r_x
                    if r_y<temp_list[idx-7][3]:
                        temp_list[idx-7][3]=r_y
                    #print(temp_list[idx-7][4])
                    if r_y>temp_list[idx-7][4]:
                        temp_list[idx-7][4]=r_y
                    # 连续匹配的文字坐标的坐标偏移不能超过2像素
                    if temp_list[idx-7][4]-temp_list[idx-7][3]>2 or temp_list[idx-7][2]-temp_list[idx-7][1]>2:
                        temp_list[idx-7]=[-1,1920,0,1080,0,None]
                else:
                    temp_list[idx-7]=[num,r_x,r_x,r_y,r_y,None]
                # 匹配上后的第20帧取出来用来匹配英雄
                if num-temp_list[idx-7][0]==20:
                    temp_list[idx-7][-1]=frame
            else:
                # 连续50帧匹配上
                if temp_list[idx-7][0]!=-1 and num-temp_list[idx-7][0]>50:
                    frame=temp_list[idx-7][-1]
                    cv2.imwrite('.\\temp\\'+str(num)+'_'+str(idx)+'.png',frame)
                    print(temp_list[idx-7][:-1])
                    # 一塔
                    if idx==15:
                        temp_y=(temp_list[8][3]+temp_list[8][4])//2
                        temp_x=(temp_list[8][1]+temp_list[8][2])//2
                        im=word_extract(frame[temp_y:temp_y+38,temp_x-70:temp_x-35])
                        result=(c_float*3)()
                        xx1=im.shape[0]
                        yy1=im.shape[1]
                        im = im.reshape(im.shape[0] * im.shape[1])
                        # 判断是红队一塔还是蓝队一塔
                        i=yita_list[0]
                        matchtemplate(i[3],len(i[2])//2,i[4][0],i[4][1],cast(im.ctypes.data,POINTER(c_int)),xx1,yy1,result)
                        r_blue=result[0]
                        i=yita_list[1]
                        matchtemplate(i[3],len(i[2])//2,i[4][0],i[4][1],cast(im.ctypes.data,POINTER(c_int)),xx1,yy1,result)
                        r_red=result[0]
                        tem=match_heroes(frame[210:275,707:772],heroes_55,False)
                        if r_blue>r_red:
                            final_result[-1].append((temp_list[8][0],'blue',tem[0]))
                        else:
                            final_result[-1].append((temp_list[8][0],'red',tem[0]))
                    # 纳什男爵，峡谷先锋，和小龙，匹配英雄头像
                    elif idx>=12:
                        temp_y=(temp_list[idx-7][3]+temp_list[idx-7][4])//2
                        temp_x=(temp_list[idx-7][1]+temp_list[idx-7][2])//2
                        tem=match_heroes(frame[210:275,temp_x-220:temp_x-155],heroes_55,False)
                        final_result[idx-5].append((temp_list[idx-7][0],tem[0]))
                    # 一血，匹配英雄头像
                    elif idx==10:
                        tem=match_heroes(frame[139:214,923:998],heroes_55,False)
                        final_result[idx-5].append((temp_list[idx-7][0],tem[0]))
                    # 五杀，匹配英雄头像
                    elif idx==9:
                        tem=match_heroes(frame[128:213,917:1002],heroes_65,False)
                        final_result[idx-5].append((temp_list[idx-7][0],tem[0]))
                    # 三杀，四杀和超神，匹配击杀者和被杀者
                    else:
                        temp_y=(temp_list[idx-7][3]+temp_list[idx-7][4])//2
                        temp_x=(temp_list[idx-7][1]+temp_list[idx-7][2])//2
                        temp_x_right=temp_x+i[4][1]
                        # 三杀，四杀
                        if idx in (7,8):
                            x_left=temp_x-hero_word_x_diff[idx-7][0]
                            x_right=temp_x+hero_word_x_diff[idx-7][1]
                        # 超神
                        else:
                            x_left=405
                            x_right=temp_x+hero_word_x_diff[idx-7][1]
                        tem_l=match_heroes(frame[210:275,x_left-5:x_left+60],heroes_55,False)
                        tem_r=match_heroes(frame[210:275,x_right-5:x_right+60],heroes_55,False)
                        final_result[idx-5].append((temp_list[idx-7][0],tem_l[0],tem_r[0]))
                    print(final_result)
                temp_list[idx-7]=[-1,1920,0,1080,0,None]
    num+=1

#记录写到文件里
filet=open('temp_zwb.txt','w')
for idx,i in enumerate(all_result):
    print(all_pic_list[idx][0])
    filet.write(all_pic_list[idx][0])
    filet.write('\n')
    for f,j in enumerate(i,1):
        print(f,j)
        filet.write(str(f)+' '+str(j)+'\n')
    print('-'*100)
    filet.write('-'*100+'\n')
filet.write(str(final_result))
filet.close()

print(final_result)

