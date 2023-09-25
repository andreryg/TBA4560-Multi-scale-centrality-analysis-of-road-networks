import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

def read_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return tree, root

def process_element_tolist(element):
    def process_element(element):

        #print(f"Element: {element.tag}, Attributes: {element.attrib}, Text: {element.text}")
        nonlocal element_list
        if "fylkesnummer" in element.tag or "stemmekretsnummer" in element.tag or "kommunenummer" in element.tag or "posList" in element.tag or "stemmekretsnavn" in element.tag:
            element_list.append(element.text)

        for child in element:
            process_element(child)

    element_list = []
    process_element(element)
    return element_list
    

def xml_to_pandas(file):
    tree, root = read_xml(file)
    elements_list = []
    i=0
    for element in root:
        if "boundedBy" not in element.tag:
            element_list = process_element_tolist(element)
            elements_list.append(dict((v,element_list[i]) for i,v in enumerate(['posList', 'Stemmekretsnummer', 'Stemmekretsnavn', 'Kommunenummer', 'Fylkesnummer'])))
        if i == 4:
            break
        i += 1
    elements = pd.DataFrame(elements_list, columns=['posList', 'Stemmekretsnummer', 'Stemmekretsnavn', 'Kommunenummer', 'Fylkesnummer'])
    print(elements)

xml_to_pandas("Basisdata_stemmekrets_områder.xml")

