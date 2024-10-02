import os,json
from shapely.geometry import Polygon

def find_polygon_center(polygon):

    if not isinstance(polygon, Polygon):
        polygon = Polygon(polygon)

    center = polygon.centroid
    return center.x, center.y

def update_coco_with_retina_keypoint(coco_data):
    clsid_name = {}
    categorylist = coco_data['categories']
    imagelist = coco_data['images']
    ann_id=1
    img_id=1
    annot_list=[]
    new_img_list=[]

    for im  in imagelist:
        imCpy={
            "id": img_id,
            "license": 1,
            "file_name": im["file_name"],
            "height": im["height"],
            "width": im["width"],
            "date_captured": "2024-05-13T06:25:49+00:00"
        }
        new_img_list.append(imCpy)
        img_id+=1

    for ct in categorylist:
        catname = ct['name']
        clsid_name[ ct['id'] ] = catname

    for annotation in coco_data['annotations']:
        annCpy=annotation.copy()
        clsName=clsid_name[annotation["category_id"]]

        if clsName=="pupil":        
            segmentation=annotation["segmentation"][0]
            segmentation=list((segmentation[i],segmentation[i+1]) for i in range(0,len(segmentation),2))
            xmin=min([i[0] for i in segmentation])
            ymin=min([i[1] for i in segmentation])
            xmax=max([i[0] for i in segmentation])
            ymax=max([i[1] for i in segmentation])
            bw=xmax-xmin
            bh=ymax-ymin
            annCpy["id"]=ann_id
            annCpy["image_id"]=annotation["image_id"]+1
            annCpy["category_id"]=1
            annCpy["bbox"]=[xmin,ymin,bw,bh]
            annCpy["area"]=annotation["area"]
            annCpy["segmentation"]=[]
            annCpy["iscrowd"]=annotation["iscrowd"]
            x,y=find_polygon_center(segmentation)
            annCpy['keypoints'] = [x, y, 2]
            annCpy['num_keypoints'] = 1  # Since we have 1 keypoint (retina)
            annot_list.append(annCpy)
            ann_id+=1

    coco_data['images']=new_img_list
    coco_data['categories']=[        {
            "id": 1,
            "name": "pupil",
            "supercategory": "Baby-eyes"
        }]
    coco_data["annotations"]=annot_list

    return coco_data

cPath = os.getcwd()
inputPar = os.path.join(cPath,'test.v3i.coco-segmentation')
outputPar = os.path.join(cPath,r'Updated_v2')
folders=os.listdir(inputPar)

for folder in folders:

    if folder in ["test","train","valid"]:
        inputChild = os.path.join(inputPar,folder)
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
                
                coco_data=update_coco_with_retina_keypoint(data)
                output_file=os.path.join(outputChild,"annotations_v2.json")

                with open(output_file, 'w') as f:
                    json.dump(coco_data, f, indent=4)
