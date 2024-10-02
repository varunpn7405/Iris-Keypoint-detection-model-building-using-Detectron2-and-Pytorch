import os,json

def bbox_to_single_keypoint(bbox):
    # bbox is in the format [x_min, y_min, width, height]
    x_min, y_min, width, height = bbox
    center_x = x_min + (width / 2)
    center_y = y_min + (height / 2)
    
    # Create a single keypoint with visibility 2 (visible and labeled)
    keypoint = [center_x, center_y, 2]
    
    return keypoint

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

    # Add a single keypoint field for each annotation

    for annotation in coco_data['annotations']:
        annCpy=annotation.copy()
        clsName=clsid_name[annotation["category_id"]]

        if clsName=="pupil":        
            annCpy["id"]=ann_id
            annCpy["image_id"]=annotation["image_id"]+1
            annCpy["category_id"]=1
            bbox = annotation['bbox']
            annCpy["bbox"]=bbox
            keypoint = bbox_to_single_keypoint(bbox)
            annCpy["area"]=annotation["area"]
            annCpy["segmentation"]=annotation["segmentation"]
            annCpy["iscrowd"]=annotation["iscrowd"]
            annCpy['keypoints'] = keypoint
            annCpy['num_keypoints'] = 1  # Since we have 1 keypoint (retina)
            annot_list.append(annCpy)
            ann_id+=1

    coco_data['images']=new_img_list
    coco_data['categories']=[{
            "id": 1,
            "name": "pupil",
            "supercategory": "Baby-eyes"
        }]
    coco_data["annotations"]=annot_list

    return coco_data


cPath = os.getcwd()
inputPar = os.path.join(cPath,'Eye_detection.v3i.coco')
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
                output_file=os.path.join(outputChild,"annotations_v1.json")

                with open(output_file, 'w') as f:
                    json.dump(coco_data, f, indent=4)
