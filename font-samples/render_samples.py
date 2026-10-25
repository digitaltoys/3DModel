from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path(__file__).resolve().parent
ui='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
label=ImageFont.truetype(ui,30,index=1)
small=ImageFont.truetype(ui,22,index=1)
title=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',44,index=1)
fonts=[('1','주아체 · 현재','jua-Jua-Regular.ttf'),('2','배민 한나체','hanna-BM-HANNA.ttf'),('3','도현체','dohyeon-DoHyeon-Regular.ttf'),('4','구기체','gugi-Gugi-Regular.ttf'),('5','검은고딕','blackhansans-BlackHanSans-Regular.ttf'),('6','감자꽃체','gamjaflower-GamjaFlower-Regular.ttf')]
im=Image.new('RGB',(1400,1320),'#fffaf8');d=ImageDraw.Draw(im)
d.text((65,40),'민결 · 한글 폰트 비교',font=title,fill='#3b3033')
d.text((67,108),'글자 높이를 맞춘 원래 폰트 형태입니다. 양각·획 보정은 적용하지 않았습니다.',font=small,fill='#806c73')
for i,(num,name,file) in enumerate(fonts):
 col=i%2;row=i//2;x=55+col*675;y=180+row*365
 d.rounded_rectangle((x,y,x+640,y+335),radius=22,fill='white',outline='#eadde1',width=2)
 d.rounded_rectangle((x+22,y+20,x+72,y+67),radius=12,fill='#f4d3dc')
 d.text((x+47,y+20),num,font=label,fill='#61384a',anchor='mt')
 d.text((x+90,y+24),name,font=label,fill='#4e3b43')
 font=ImageFont.truetype(str(p/file),320)
 bbox=font.getbbox('민결');mask=Image.new('L',(bbox[2]-bbox[0]+12,bbox[3]-bbox[1]+12))
 ImageDraw.Draw(mask).text((6-bbox[0],6-bbox[1]),'민결',font=font,fill=255)
 mask=mask.crop(mask.getbbox());h=172;w=round(mask.width*h/mask.height)
 if w>555:w=555;h=round(mask.height*w/mask.width)
 mask=mask.resize((w,h),Image.Resampling.LANCZOS)
 im.paste('#b65c7b',(x+(640-w)//2,y+113+(180-h)//2),mask)
im.save(p/'korean-font-comparison.png')
