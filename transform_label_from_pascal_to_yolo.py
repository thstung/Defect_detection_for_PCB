import os
from xml.etree.ElementTree import ElementTree,Element

url_annotations = "Augmentation_PCB/voc_annotations"
url_save_annotation = "Augmentation_PCB/yolo_annotations"
WIDTH, HEIGHT = 600, 600

def read_xml(in_path):
    # in_path: .xml
    # return: ElementTree
    tree = ElementTree()
    tree.parse(in_path)
    return tree

def trans_defect_name_2_num(defect_name):
    if defect_name == 'missing_hole':
        return 0
    elif defect_name == 'mouse_bite':
        return 1
    elif defect_name == 'open_circuit':
        return 2
    elif defect_name == 'short':
        return 3
    elif defect_name == 'spur':
        return 4
    else:
        return 5


for item in os.listdir(url_annotations):
    bboxes = []
    tree = read_xml(url_annotations + "/" + item)
    root = tree.getroot()
    object = root.findall("object")
    if object == None:
        print(item)
        continue
    for it in object:
        defect_label = it.find("name").text
        num_defect = trans_defect_name_2_num(defect_label)
        bndbox = it.find("bndbox")
        if bndbox == None:
            print(item)
        xmin = float(bndbox.find("xmin").text)
        xmax = float(bndbox.find("xmax").text)
        ymin = float(bndbox.find("ymin").text)
        ymax = float(bndbox.find("ymax").text)
        bboxes.append([str(num_defect), str((xmin+xmax)/(2*WIDTH)), str((ymin+ymax)/(2*HEIGHT)), str((xmax - xmin)/WIDTH), str((ymax - ymin)/HEIGHT)])
    txtfile = open(url_save_annotation + '/' + item[:-4] + '.txt', "w")
    for bbox in bboxes:
        txtfile.writelines(' '.join(bbox))
        txtfile.write('\n')
        print(bbox)
    txtfile.close()