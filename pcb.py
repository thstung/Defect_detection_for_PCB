import numpy
import os

class PCB:
    def __init__(self, name, url_image, id):
        self.url_image = url_image
        self.id = id
        self.name = name
        self.label = []
        self.image_process = numpy.array([])
        self.is_process = False
        self.status = 'white'

    def getStatus(self):
        if self.is_process:
            defect = [0, 0, 0, 0, 0, 0]
            for label in self.getPCBLabel():
                defect[label[0]] = defect[label[0]] + 1
            if defect[1] != 0 or defect[2] != 0 or defect[3] != 0:
                self.status = '#FF3333'
            elif defect[0] != 0 or defect[4] != 0 or defect[5] != 0:
                self.status = 'yellow'
            else:
                self.status = 'green2'
        return self.status

    def getPCBLabel(self):
        new_label = []
        for label in self.label:
            new_label.append([int(label[5]), round(float(label[4]), 2), int(label[0]),
                              int(label[1]), int(label[2]), int(label[3])])
        return new_label

