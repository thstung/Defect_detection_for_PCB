import albumentations as A
# import random
import cv2
import os
# import shutil
# import random
# import math
from xml.etree.ElementTree import ElementTree,Element
# from matplotlib import pyplot as plt
from xml.dom import minidom
from albumentations.augmentations.functional import transpose

WIDTH, HEIGHT = 600, 600

def read_xml(in_path):
    # in_path: .xml
    # return: ElementTree
    tree = ElementTree()
    tree.parse(in_path)
    return tree

def random_crop(image, bboxes, tranform):
    transformed = transform(image=image, bboxes=bboxes)
    return transformed

def create_xml_voc(file_name, bboxes, w_img, h_img):
    # create a xml document
    root = minidom.Document()
    # create annotation tag as root tag
    annotation = root.createElement('annotation')
    root.appendChild(annotation)

    # create child tag of annotation tag
    folder = root.createElement('folder')
    folder_text = root.createTextNode("Augmentation_PCB")
    folder.appendChild(folder_text)
    annotation.appendChild(folder)
    filename = root.createElement('filename')
    filename_text = root.createTextNode(file_name)
    filename.appendChild(filename_text)
    annotation.appendChild(filename)

    # create child tag of annotation tag
    size = root.createElement('size')
    width = root.createElement("width")
    width_text = root.createTextNode(str(w_img))
    width.appendChild(width_text)
    size.appendChild(width)
    height = root.createElement("height")
    height_text = root.createTextNode(str(h_img))
    height.appendChild(height_text)
    size.appendChild(height)
    depth = root.createElement("depth")
    depth_text = root.createTextNode('3')
    depth.appendChild(depth_text)
    size.appendChild(depth)
    annotation.appendChild(size)

    # create object tag of annotation tag
    for bbox in bboxes:
        bbox_object = root.createElement('object')
        name = root.createElement('name')
        name_text = root.createTextNode(bbox[4])
        name.appendChild(name_text)
        bbox_object.appendChild(name)
        annotation.appendChild(bbox_object)
        # create bound box tag of object tag
        bndbox = root.createElement('bndbox')
        xmin = root.createElement('xmin')
        xmin_text = root.createTextNode(str(int(round(bbox[0], 0))))
        xmin.appendChild(xmin_text)
        bndbox.appendChild(xmin)

        ymin = root.createElement('ymin')
        ymin_text = root.createTextNode(str(int(round(bbox[1], 0))))
        ymin.appendChild(ymin_text)
        bndbox.appendChild(ymin)

        xmax = root.createElement('xmax')
        xmax_text = root.createTextNode(str(int(round(bbox[2], 0))))
        xmax.appendChild(xmax_text)
        bndbox.appendChild(xmax)

        ymax = root.createElement('ymax')
        ymax_text = root.createTextNode(str(int(round(bbox[3], 0))))
        ymax.appendChild(ymax_text)
        bndbox.appendChild(ymax)
        bbox_object.appendChild(bndbox)

    mydata = root.toprettyxml(indent="\t")
    return mydata

transform = A.Compose([
        A.RandomCrop(width = WIDTH, height = HEIGHT),
        A.HorizontalFlip(p=0.5)
    ], bbox_params=A.BboxParams(format='pascal_voc'))

url_annotations = "PCB_DATASET/Annotations"
url_images = "PCB_DATASET/images"
url_save_annotation = "Augmentation_PCB/voc_annotations"
url_save_image = "Augmentation_PCB/images"
for folder_name in os.listdir(url_annotations):
    new_url_annotations = url_annotations + '/' + folder_name
    for item in os.listdir(new_url_annotations):
        bboxes = []
        tree = read_xml(new_url_annotations + "/" + item)
        root = tree.getroot()
        image_name = root.find("filename").text
        image = cv2.imread(url_images + '/' + folder_name + '/' + image_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        object = root.findall("object")
        if object == None:
            print(item)
            continue
        for it in object:
            defect_label = it.find("name").text
            bndbox = it.find("bndbox")
            if bndbox == None:
                print(item)
            xmin = int(bndbox.find("xmin").text)
            xmax = int(bndbox.find("xmax").text)
            ymin = int(bndbox.find("ymin").text)
            ymax = int(bndbox.find("ymax").text)
            bboxes.append([xmin, ymin, xmax, ymax, defect_label])
            index = 0
        while index < 20:
            transformed = random_crop(image, bboxes, transform)
            transformed_image = transformed["image"]
            transformed_bboxes = transformed["bboxes"]
            print(transformed_bboxes)
            if len(transformed_bboxes) == 0:
                continue
            mydata = create_xml_voc(item[:-4] + '_' + str(index) + '_' + str(WIDTH) + 'x' + str(HEIGHT) + '.jpg',  transformed_bboxes, WIDTH, HEIGHT)
            myxmlfile = open(url_save_annotation + '/' + item[:-4]+ '_' + str(index) + '_' + str(WIDTH) + 'x' + str(HEIGHT) + '.xml', "w")
            myxmlfile.write(mydata)
            myxmlfile.close()
            cv2.imwrite(url_save_image + '/' + item[:-4] + '_' + str(index) + '_' + str(WIDTH) + 'x' + str(HEIGHT) + '.jpg', transformed_image)
            index = index + 1