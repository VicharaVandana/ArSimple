'''
This Script will take a arxml file
and generate simple xml file
'''

import xmltodict
import xml.etree.ElementTree as ET
from xml.dom import minidom

Ecuc_ContainerList = [] #list of all ECUC containers of our interest
Ecuc_ParamValList = []  #list of all ECUC parameters of our interest
Ecuc_ParamRefList = []  #list of all ECUC references of our interest

Shortnamelist = {}

def updatexpath(instr):
    newlist = []
    oldlist = instr.split("/")  #split the xpath into elements
    for element in oldlist: #for each element check if its present as key in shortnamelist dictionary. 
        if element in Shortnamelist:    #if present the replcace it with updated shortname
            newlist.append(Shortnamelist[element])
        else:   #else keep the old name only.
            newlist.append(element)
            
    outstr = '/'.join(newlist)  #join all the elements to make ew xpath
    return(outstr)  #return the new xpath


def UpdateList(MyDict):
    if "DEFINITION-REF" in MyDict:
        dest = MyDict["DEFINITION-REF"]["@DEST"]
        dest_parts = dest.split("-")
        #if the definition is container type(1)
        if ((dest == "ECUC-PARAM-CONF-CONTAINER-DEF")):
            Shortnamelist[(((MyDict["DEFINITION-REF"]["#text"]).split('/'))[-1])] = (MyDict["SHORT-NAME"])
            Ecuc_ContainerList.append({"type":(((MyDict["DEFINITION-REF"]["#text"]).split('/'))[-1]),"xpath":updatexpath(MyDict["DEFINITION-REF"]["#text"])})
            #print(Shortnamelist.popitem())
        #If the definition is parameter value type(2)
        elif ((dest_parts[0] == "ECUC") and (dest_parts[-1] == "DEF") and (dest_parts[-2] == "PARAM")):
            Ecuc_ParamValList.append({"type":dest[5:-10],"value":MyDict["VALUE"],"xpath":updatexpath(MyDict["DEFINITION-REF"]["#text"])})

        #If the definition is reference type(3)
        elif ((dest_parts[0] == "ECUC") and (dest_parts[-1] == "DEF") and (dest_parts[-2] == "REFERENCE")):
            Ecuc_ParamRefList.append({"type":dest[5:-4],"value":MyDict["VALUE-REF"]["#text"],"xpath":updatexpath(MyDict["DEFINITION-REF"]["#text"])})


'''             
collect data.
There are 3 types of datas.
1) containers: which will result in elements with child elements.
2) parameter values: which are the elements with the value
3) parameter Reference values: whch are elements which has reference to another element in xml as its value

'''
def CollectData(d):
    for k, v in d.items():
        if isinstance(v, dict):
            UpdateList(v)                   
            CollectData(v)
            
        elif isinstance(v, list):
            for lv in v:
                if isinstance(lv, dict):
                    UpdateList(lv)    
                    CollectData(lv)
        

def Update_SimpleXML_Containers(mydict):
    #get the string
    pathstr = mydict['xpath'][1:]   #extracting the xpath string
    typestr = mydict['type']
    nodenames = pathstr.split("/")      #all the nodes in the string are got in a list
    finalnodename = nodenames.pop()         #last node is extracted.
    nodenames.remove(rootname)          #removing the root node

    '''
    Parse through each node and search if the node exist in the ElementTree
    if exists then make that the parent node and move to next node
    if it doesnt exist then create the node under current parent node
    and make it the new parent node
    '''
    parentnode = root           #initially the root is the parent where the search begin
    for nodename in nodenames:
        node = parentnode.find(nodename)    #try fetching the child node
        if (node == None):  #if the child doesnt exist 
            childnode = ET.SubElement(parentnode, nodename) #create that node
            parentnode = childnode      #make this child node the new parent node
        else:   #if the node exists
            parentnode = node   #make the node as parent node and move further down
    #end of for loop

    finalnode = ET.SubElement(parentnode, finalnodename)    #creates the tag
    finalnode.set("name", typestr)        #creates the attributes
    
########################## end of Update_SimpleXML_Containers() ########################################

def Update_SimpleXML_ParamVal(mydict):
    #get the string
    pathstr = mydict['xpath'][1:]   #extracting the xpath string
    typestr = mydict['type']        #extracting the type
    value = mydict['value']          #extracting the value
    nodenames = pathstr.split("/")      #all the nodes in the string are got in a list
    finalnodename = nodenames.pop()         #last node is extracted.
    nodenames.remove(rootname)          #removing the root node

    '''
    Parse through each node and search if the node exist in the ElementTree
    if exists then make that the parent node and move to next node
    if it doesnt exist then create the node under current parent node
    and make it the new parent node
    '''
    parentnode = root           #initially the root is the parent where the search begin
    for nodename in nodenames:
        node = parentnode.find(nodename)    #try fetching the child node
        if (node == None):  #if the child doesnt exist 
            childnode = ET.SubElement(parentnode, nodename) #create that node
            parentnode = childnode      #make this child node the new parent node
        else:   #if the node exists
            parentnode = node   #make the node as parent node and move further down
    #end of for loop

    paramvalnode = ET.SubElement(parentnode, finalnodename)    #creates the tag
    paramvalnode.set("type", typestr)        #creates the attributes
    paramvalnode.set("contains", "VALUE")        #creates the attributes

    paramvalnode.text = value           #adds the value to the node. (content of the element)
    
########################## end of Update_SimpleXML_ParamVal() ########################################


def Update_SimpleXML_ParamRef(mydict):
    #get the string
    pathstr = mydict['xpath'][1:]   #extracting the xpath string
    typestr = mydict['type']        #extracting the type
    ref = mydict['value']          #extracting the reference value
    nodenames = pathstr.split("/")      #all the nodes in the string are got in a list
    finalnodename = nodenames.pop()         #last node is extracted.
    nodenames.remove(rootname)          #removing the root node

    '''
    Parse through each node and search if the node exist in the ElementTree
    if exists then make that the parent node and move to next node
    if it doesnt exist then create the node under current parent node
    and make it the new parent node
    '''
    parentnode = root           #initially the root is the parent where the search begin
    for nodename in nodenames:
        node = parentnode.find(nodename)    #try fetching the child node
        if (node == None):  #if the child doesnt exist 
            childnode = ET.SubElement(parentnode, nodename) #create that node
            parentnode = childnode      #make this child node the new parent node
        else:   #if the node exists
            parentnode = node   #make the node as parent node and move further down
    #end of for loop

    paramrefnode = ET.SubElement(parentnode, finalnodename)    #creates the tag
    paramrefnode.set("type", typestr)        #creates the attributes
    paramrefnode.set("contains", "REFERENCE")        #creates the attributes

    paramrefnode.text = ref.replace(refrootname,rootname)  #adds the value to the node. (content of the element)
    
    
########################## end of Update_SimpleXML_ParamRef() ########################################   

#Reading the arxml file
with open('smallarxmldcm.xml', 'r') as myfile:
#with open('HKMC_Mercury_Dcm_ecuc.arxml', 'r') as myfile:
    data = myfile.read() 

my_dict = xmltodict.parse(data) #convert the arxml to dictionary

CollectData(my_dict)    #Extract required containers parameter values and references from arxml dictionary

#Here the creating SimpleXML part from lists starts
rootname = Ecuc_ContainerList[0]['xpath'].split("/")[1] #extracting the root element name

refrootname = Ecuc_ParamRefList[0]['value'].split("/")[1] #extracting the references root name


# build a tree structure
root = ET.Element(rootname)

#populating the containers part for SimpleXML
for container in Ecuc_ContainerList:
    Update_SimpleXML_Containers(container)
    
#populating the parameter values part for SimpleXML
for parameter in Ecuc_ParamValList:
    Update_SimpleXML_ParamVal(parameter)

#populating the parameter references part for SimpleXML
for reference in Ecuc_ParamRefList:
    Update_SimpleXML_ParamRef(reference)

#swap the name attribute with tag for the elements
for container in root.iter():
    name = container.get('name')
    if (name != None):  #if name attribute is there, then swap the tag namd and attribute
        container.set("name", container.tag)
        container.tag = name

xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
with open("ArSimple.xml", "w") as f:
    f.write(xmlstr)

'''
print(Ecuc_ContainerList)
print("HAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHA")
print(Ecuc_ParamValList)
print("HEHEHEHEHEHEHEHEHEHEHEHEHEHEHEHEHEHEHEHEHE")
print(Ecuc_ParamRefList)
'''
