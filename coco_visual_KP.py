import os,json, random
from PIL import Image,ImageDraw,ImageFont

font = ImageFont.truetype("arial.ttf", 15)
path = os.getcwd()
inputPar = os.path.join(path,'dataset')
outputPar = os.path.join(path,r'Visualization')

if not os.path.exists(outputPar):
    os.makedirs(outputPar)

folders = os.listdir(inputPar)
cls_color={}

for folder in folders:
    inputChild = os.path.join(inputPar,folder,"annotations")
    outputChild = os.path.join(outputPar,folder)
    
    if not os.path.exists(outputChild):
        os.makedirs(outputChild)

    files = os.listdir(inputChild)
    
    for file in files:
        fname, ext = os.path.splitext(file)

        if ext.lower()==".json":
            finput = os.path.join(inputChild,file)

            with open(finput) as cj:
                data = json.load(cj)

            imgid_name = {}
            imgids = []
            imagelist = data['images']

            for im  in imagelist:
                imgid_name[ im['id'] ] = str(im['file_name'])
                imgids.append(im['id'])

            clsid_name = {}
            categorylist = data['categories']

            for ct in categorylist:
                catname = ct['name']
                clsid_name[ ct['id'] ] = catname
                if catname not in cls_color:
                    cls_color[ct['name']]= "#%06X" % random.randint(0, 0xFFFFFF)
                
            annotations = data['annotations']

            for id in imgids:
                imgName = imgid_name[id]
                fname,ext=os.path.splitext(imgName)
                imgPath = os.path.join(inputPar,folder,"images",imgName)

                if os.path.exists(imgPath):
                    print("Plotting_____",imgName)
                    img = Image.open(imgPath)
                    imgcopy = img.copy()
                    draw = ImageDraw.Draw(img)

                    for ann in annotations:

                        if ann['image_id'] == id:
                            bbx=ann["bbox"]

                            bxmin,bymin,box_w,box_h=ann["bbox"]
                            draw.rectangle((bxmin,bymin,bxmin+box_w,bymin+box_h), outline= "red",width = 1)
                            clsName = clsid_name[ann['category_id']]
                            color=cls_color[clsName]
                            xmin,ymin,vis=ann['keypoints']
                            cls_txt =f"{clsName}"
                            bw,bh = font.getbbox(cls_txt)[2:]
                            txtbox = [(xmin,ymin-bh),(xmin+bw,ymin)]
                            draw.rectangle((xmin,ymin,xmin+2,ymin+2),fill=color)
                            draw.rectangle(txtbox, fill=color)
                            draw.text((xmin,ymin-bh),cls_txt,fill='white',font=font)
                                
                    fout = os.path.join(outputChild,imgName)
                    img.save(fout)
                
                else:
                    print("not found",imgPath)
print(cls_color)
