import os,json
import natsort

path = os.getcwd()
inputPar = os.path.join(path,"dataset(keras)")
outPar = os.path.join(path,'Output_v1')

if not os.path.exists(outPar):
    os.makedirs(outPar)

empty=0
timg  = tcntr = tbox = 0

folders = natsort.natsorted(os.listdir(inputPar))

for folder in folders:
    if folder=="annotations":
        fimg = fcntr = fbox = 0
        final_result = {
                        "licenses": [{
                                            "name": "",
                                            "id": 0,
                                            "url": ""
                                        }],
                        "info": {
                            "contributor": "",
                            "date_created": "",
                            "description": "",
                            "url": "",
                            "version": "",
                            "year": ""
                        },
                        "categories" :[
                                        {
                                            "id": 1,
                                            "name": "pupil",
                                            "supercategory": "Baby-eyes"
                                        }
                                    ],
                        "images" : [],
                        "annotations" : [],
        }

        img_id = 1
        ann_id = 1
        img_nameId = {}
        cat_nameId = {}

        for cat in final_result['categories']:
            cat_nameId[cat['name']] = cat['id']


        inputChild = os.path.join(inputPar,folder)
        outChild = os.path.join(outPar,folder)
        if not os.path.exists(outChild):
            os.makedirs(outChild)

        files = os.listdir(inputChild)
        for file in files:
            finput = os.path.join(inputChild,file)
            with open(finput) as f:
                data = json.load(f)


            imgIdName = {}
            images = data['images']
            for img in images:
                timg+=1
                fimg+=1
                imgname = img['file_name']
                imgIdName[img['id']] = img['file_name']
                img_copy = img.copy()
                img_copy['id'] = img_id
                img_nameId[imgname] = img_id
                img_id+=1
                final_result['images'].append(img_copy)

            cat_idName = {}
            flcategories = data['categories']
            for flcat in flcategories:
                cat_idName[flcat['id']] = flcat['name']
            
            annotations = data['annotations']
            
            for ann in annotations:
                if ann['segmentation']:
                    tcntr+=1
                    fcntr+=1
                if not ann["segmentation"]:
                    empty+=1

                else:
                    tbox+=1
                    fbox+=1

                imgname = imgIdName[ann['image_id']]
                new_imgId = img_nameId[imgname]
                cat_name = cat_idName[ann['category_id']]
                new_catId = cat_nameId[cat_name]

                ann_copy = ann.copy()
                ann_copy['id'] = ann_id
                ann_copy['image_id'] = new_imgId
                ann_copy['category_id'] = new_catId
                ann_id+=1
                final_result['annotations'].append(ann_copy)

        fout = os.path.join(outChild,f"instances_default.json")
        with open(fout,'w') as f:
            json.dump(final_result,f,indent=4)
        
        print(f"{folder} >> images: {fimg}  contour: {fcntr}  bbox: {fbox}")

# print(f"\nTotal images: {timg}  empty: {empty}  annotations: {tcntr} ")

print('\nTotal frames:',timg,'  empty:',empty,'  annotations:',tcntr)
