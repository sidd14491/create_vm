from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import time


TAG_PARAMS = ['name','uuid','memory','currentMemory','vcpu','resource','os', \
                'features','cpu','clock','on_poweroff','on_reboot','on_crash', \
                'pm','devices','seclabel']
DEVICE = ['emulator', 'disk','controller','interface','serial','console',\
                'input', 'graphics','sound','video','redirdev','memballoon']
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def root_element(vm_name=None):
        id_value= str(len(vm_name))
        top = Element('domain')
        top.set('type','kvm');top.set('id',id_value)
        return top
def set_basic_tag_name(set_text):
        #top = root_element()
        for tag in TAG_PARAMS:
                SubElement(set_text, tag)#;top._children[0].text='OOO'
        return set_text
def set_first_level_value_tag(vm_name=None,set_text=None):
        uuid = str(len(vm_name)+10)
        for key in set_text._children:
                if key.tag == 'name':
                        key.text = vm_name
                if key.tag == 'uuid':
                         key.text = '0d6b7f2c-1839-41cc-bd18-228b1ac3e9%s'%uuid
                if key.tag == 'memory' or key.tag == 'currentMemory':
                        key.set('unit','KiB')
                        key.text = '4194304'
                if key.tag == 'vcpu':
                        key.set('placement','static')
                        key.text = '3'
                if key.tag == 'on_poweroff':
                        key.text = 'destroy'
                if key.tag == 'on_reboot'or key.tag == 'on_crash':
                        key.text = 'restart'
        return set_text
def set_second_level_value_tag(set_text):
        for key in set_text._children:
                if key.tag == 'resource':
                        SubElement(key,'partition')
                        key._children[0].text = '/machine'
                if key.tag == 'os':os_type = SubElement(key,'type', {'arch':'x86_64','machine':'pc-i440fx-xenial'})
                        os_type.text = 'hvm'
                        SubElement(key,'boot');key._children[1].set('dev','hd')
                if key.tag == 'features':
                        SubElement(key,'acpi')
                        SubElement(key,'apic')
                if key.tag == 'cpu':
                        key.set('mode','custom')
                        key.set('match','exact')
                        SubElement(key,'model',{'fallback':'allow'});key._children[0].text='Haswell-noTSX-IBRS'
                if key.tag == 'clock':
                        SubElement(key,'timer');key._children[0].set('name','rtc');key._children[0].set('tickpolicy','catchup')
                        SubElement(key,'timer');key._children[1].set('name','pit');key._children[1].set('tickpolicy','delay')
                        SubElement(key,'timer');key._children[2].set('name','hpet');key._children[2].set('present','no')
                if key.tag == 'pm':
                        SubElement(key,'suspend-to-mem');key._children[0].set('enabled','no')
                        SubElement(key,'suspend-to-disk');key._children[1].set('enabled','no')
                if key.tag == 'seclabel':
                        key.set('type','dynamic');key.set(' model','apparmor');key.set('relabel','yes')
                        SubElement(key,'label') # Pending to add TEXT
                        SubElement(key,'imagelabel') # Pending to add TEXT
        return set_text

def set_device_tag_value(vm_name=None,set_text=None,count=None):
        for key in set_text._children:
            if key.tag == 'devices':
                for device_tag in DEVICE:
                    if device_tag == 'emulator':
                        emul = SubElement(key,device_tag)
                        emul.text = '/usr/bin/kvm-spice'
                    elif device_tag == 'disk':
                        set_device_disk(vm_name=vm_name,set_text=set_text)
                    elif device_tag == 'interface':
                        set_interface_disk(vm_name=vm_name,set_text=set_text,count=count)
                    elif device_tag == 'controller':
                        set_controller_device(set_text)
                    else:
                         set_device_resparams(set_text, device_tag,count=count)
        return set_text
def  set_controller_device(set_text):
        for key in set_text._children:
             if key.tag == 'devices':
                cont = SubElement(key,'controller',{'type':'usb','index':'0','model':'ich9-ehci1'})
                SubElement(cont,'alias',{'name':'usb'})
                SubElement(cont, 'address', {'type':'pci','domain':'0x0000','bus':'0x00','slot':'0x09','function':'0x7'})
                cont1 =  SubElement(key,'controller' ,{'type':'usb','index':'0','model':'ich9-uhci1'})
                SubElement(cont1, 'alias',{'name':'usb'})
                SubElement(cont1,'master', {'startport':'0'})
                SubElement(cont1, 'address',{'type':'pci','domain':'0x0000','bus':'0x00','slot':'0x09','function':'0x0','multifunction':'on'})

def  set_device_disk(vm_name=None,set_text=None):
        for key in set_text._children:for key in set_text._children:
            if key.tag == 'devices':
                      value = SubElement(key,'disk',{'type':'file','device':'disk'})
                      op = 'OOO.qcow2'
                      SubElement(value,'driver',{'name':'qemu','type':'qcow2'})
                      SubElement(value,'source',{'file':'/var/lib/libvirt/images/%s.qcow2'%vm_name})
                      SubElement(value,'backingStore')
                      SubElement(value,'alias',{'name':'virtio-disk0'})
                      SubElement(value,'target', {'dev':'vda','bus':'virtio'})
                      SubElement(value,'address', {'type':'pci','domain':'0x0000','bus':'0x00','slot':'0x0d','function':'0x0'})
        return set_text

def set_interface_disk(vm_name=None,set_text=None,count=None):
        bridge_name=create_bridge(2)
        for key in set_text._children:
           if key.tag == 'devices':
              for i in range(len(bridge_name)):
                 ran_val = (count*10)+1+i
                 slot = i+2
                 domain =i+2
                 inter = SubElement(key,'interface',{'type':'bridge'})
                 SubElement(inter,'mac',{'address':'52:54:00:0c:60:%s'%ran_val})
                 SubElement(inter,'source',{'bridge':'%s'%bridge_name[i]})
                 SubElement(inter,'target',{'dev':'vnet%s'%ran_val})
                 SubElement(inter,'model', {'type':'virtio'})
                 SubElement(inter,'alias',{'name':'net%s'%ran_val})
                 SubElement(inter,'address',{'type':'pci','domain':'0x0000','bus':'0x00','slot':'0x0%s'%slot,'function':'0x0'})
        return set_text

def set_device_resparams(set_text=None, device_tag=None,count=None):
     for key in set_text._children:
        if key.tag == 'devices':
           if device_tag == 'serial':
                   # Serial Children
                   counter = count*10
                   serial = SubElement(key,'serial',{'type':'pty'})
                   SubElement(serial, 'source',{'path':'/dev/pts/%s'%counter})
                   SubElement(serial, 'target',{'port':'0'})
                   SubElement(serial,'alias',{'name':'serial0'})
           if device_tag == 'console':
                   counter = count*10
                   # Console Children under device
                   console = SubElement(key,'console',{'type':'pty','tty':'/dev/pts/%s'%counter})
                   SubElement(console, 'source', {'path':'/dev/pts/%s'%counter})
                   SubElement(console, 'target',{'type':'serial','port':'0'})
                   SubElement(console, 'alias', {'name':'serial0'})

           if device_tag == 'channel':
                   # Channel Children under device
                   channel = SubElement(key,'channel', {'type':'spicevmc'})SubElement(channel, 'target', {'type':'virtio','name':'com.redhat.spice.0','state':'disconnected'})
                   SubElement(channel,'alias',{'name':'channel0'})
                   SubElement(channel,'address',{'type':'virtio-serial','controller':'0','bus':'0', 'port':'1'})

           if device_tag == 'input':
                   # Input Children under device
                   input_1 = SubElement(key,'input', {'type':'mouse','bus':'ps2'})
                   input_2 = SubElement(key,'input', {'type':'keyboard','bus':'ps2'})

           if device_tag == 'graphics':
                   # Graphics Children under device
                   graphics = SubElement(key,'graphics',{'type':'spice','port':'5903','autoport':'yes','listen':'127.0.0.1'})
                   SubElement(graphics,'listent', {'type':'address','address':'127.0.0.1'})
                   SubElement(graphics,'image',{'compression':'off'})

           if device_tag == 'sound':
                   # Sound Children under device
                   sound = SubElement(key,'sound',{'model':'ich6'})
                   SubElement(sound,'alias',{'name':'sound0'})
                   SubElement(sound,'address',{'type':'pci','domain':'0x0000','bus':'0x00','slot':'0x0c','function':'0x0'})

           if device_tag == 'video':
                   # Video Children under device
                   video = SubElement(key,'video')
                   SubElement(video,'model',{'type':'qxl','ram':'65536','vram':'65536','vgamem':'16384','heads':'1'})
                   SubElement(video,'alias',{'name':'video0'})
                   SubElement(video, 'address',{'type':'pci','domain':'0x0000','bus':'0x00','slot':'0x0b','function':'0x0'})
           if device_tag == 'redirdev':
                   # Redirdev Children under device
                   redirdev_0 = SubElement(key,'redirdev',{'bus':'usb','type':'spicevmc'})
                   SubElement(redirdev_0, 'alias',{'name':'redir0'})
                   redirdev_1 = SubElement(key,'redirdev',{'bus':'usb','type':'spicevmc'})
                   SubElement(redirdev_1, 'alias',{'name':'redir1'})
           if device_tag == 'memballoon':
                   # memballoon Children under device
                   memballoon = SubElement(key,'memballoon', {'model':'virtio'})
                   SubElement(memballoon, 'alias', {'name':'balloon0'})
                   SubElement(memballoon,'address',{'type':'pci','domain':'0x0000','bus':'0x00','slot':'0x0a','function':'0x0'})


def create_bridge(number):
        import commands
        bridge = ['virbr0']
        for i in range(number):
                name = "Test_Br_%s"%i
                out = commands.getoutput("brctl  addbr %s"%name)
                commands.getoutput("ifconfig %s up"%name)
                bridge.append(name)
        return bridge
vm_name_list = []
def create_qcow2():import shutil
        vm_name_list = []
        for i in range(1,2):
                if i == 1:
                        vm_name = "Mid-Rtr221343"
                elif i ==2:
                       vm_name = "Oam-Hub"
                elif i == 3:
                        vm_name = "Enter-Hub"
                elif i == 4:
                        vm_name = "Spoke-One-1"
                elif i == 5:
                        vm_name = "Spoke2"
                shutil.copy('/root/junos-vsrx3-x86-64-19.3R2-S1.qcow2', '/var/lib/libvirt/images/%s.qcow2'%vm_name)
                vm_name_list.append(vm_name)
        return vm_name_list
vm_list = create_qcow2()
def create_vm_xml():
        counter= 0
        for vm  in vm_list:
                counter+=1
                set_text=root_element(vm)
                set_text =set_basic_tag_name(set_text)
                set_text = set_first_level_value_tag(vm_name=vm,set_text=set_text)
                set_text = set_second_level_value_tag(set_text)
                set_text = set_device_tag_value(vm_name=vm,set_text=set_text,count=counter)
                vm_xml_file = "%s.xml"%vm
                mydata = ElementTree.tostring(set_text)
                myfile = open(vm_xml_file, "w")
                myfile.write(mydata)
                time.sleep(2)
import commands
def define_vm():
        for vm  in vm_list:
                vm_xml_file = "%s.xml"%vm
                out = commands.getoutput("virsh define /root/SID-AUT/%s"%vm_xml_file)
                print out
                time.sleep(3)
def start_vm():
        for vm  in vm_list:
                 import pdb;pdb.set_trace()
                 op =commands.getoutput("virsh start %s"%vm)
                 print op
create_vm_xml()
define_vm()
start_vm()
