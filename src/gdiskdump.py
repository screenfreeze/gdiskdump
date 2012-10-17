#!/usr/bin/python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2011 Andreas Wilhelm <andywilhelm@online.de>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 2, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE


import sys
try:  
    import pygtk  
    pygtk.require("2.0")  
except:  
    pass  
try:  
    import gtk  
except:  
    print("GTK Not Availible")
    sys.exit(1)

import subprocess
import gobject
import signal
import gzip
import os
import thread
import pynotify
import string
import struct
import gettext
from gettext import gettext as _
gettext.textdomain('gdiskdump')

import logging
logger = logging.getLogger('gdiskdump')

from gdiskdumpconfig import get_data_path as getdatapath


# ask for root
if os.geteuid() != 0:
    print "You must be root to run this program."
    sys.exit(1)

class gdiskdump:

    def __init__( self ):
        self.builder = gtk.Builder()
        self.builder.set_translation_domain('gdiskdump')
        self.builder.add_from_file("data/ui/GdiskdumpWindow.ui")
        self.builder.add_from_file("data/ui/AboutGdiskdumpDialog.ui")
        
        dic = { 
            "on_i_format_combobox_changed" : self.on_i_format_combobox_changed,
            "on_o_format_combobox_changed" : self.on_o_format_combobox_changed,
            "on_i_filechooserwidget_changed" : self.on_i_filechooserwidget_changed,
            "on_o_filechooserwidget_changed" : self.on_o_filechooserwidget_changed,
            "on_o_file_compression_clicked" : self.on_o_filechooserwidget_changed,
            "on_ohd_treeview_cursor_changed" : self.on_ohd_treeview_cursor_changed,
            "on_opart_treeview_cursor_changed" : self.on_opart_treeview_cursor_changed,
            "on_ihd_treeview_cursor_changed" : self.on_ihd_treeview_cursor_changed,
            "on_ipart_treeview_cursor_changed" : self.on_ipart_treeview_cursor_changed,
            "on_i_fwd_button_clicked" : self.on_i_fwd_button_clicked,
            "on_o_fwd_button_clicked" : self.on_o_fwd_button_clicked,
            "on_o_back_button_clicked" : self.on_o_back_button_clicked,
            "on_abort_dd_button_clicked" : self.on_abort_dd_button_clicked,
            "on_dd_back_button_clicked" : self.on_dd_back_button_clicked,

            "on_start_dd_button_clicked" : self.on_start_dd_button_clicked,
            "on_new_button_clicked" : self.on_new_button_clicked,
            "on_about_button_clicked" : self.about,
            "start_dd_process" : self.start_dd_process,
            "dspaceerr_ok" : self.dspaceerr_ok,
            "quit" : self.quit,
            "on_destroy" : self.on_destroy,
        }
        
        self.builder.connect_signals( dic )

        self.finish_initializing()


    def finish_initializing(self):
        self.AboutDialog = self.builder.get_object("about_gdiskdump_dialog")

        # Code for other initialization actions should be added here.
        self.input=[None,None,None,None,None]
        self.output=[None,None,None]
        self.get_partition_liststore()
        self.get_hd_liststore()
        self.datapath =getdatapath()
        filter = gtk.FileFilter()
        filter.set_name(_('All Files'))
        filter.add_pattern('*')
        self.all_filter=filter
        filter = gtk.FileFilter()
        filter.set_name('img')
        filter.add_pattern('*.tar.gz')
        filter.add_pattern('*.img.gz')
        filter.add_pattern('*.img')
        self.img_filter=filter
        filter = gtk.FileFilter()
        filter.set_name('img')
        filter.add_pattern('*')
        self.empty_img_filter=filter
        self.builder.get_object("i_filechooserwidget").add_filter(self.img_filter)
        self.builder.get_object("i_filechooserwidget").add_filter(self.all_filter)
        self.builder.get_object("o_filechooserwidget").add_filter(self.empty_img_filter)
        self.builder.get_object("o_filechooserwidget").add_filter(self.all_filter)
        print 'finished initializing' 


    def get_hd_liststore(self):
        liststore=self.builder.get_object("hd_liststore")
        process = subprocess.Popen(['fdisk','-l'],stdout=subprocess.PIPE,shell=False)
        outstr,err=process.communicate()
        pix=gtk.gdk.pixbuf_new_from_file(getdatapath() +'/media/drive-harddisk.svg')
        devlist=outstr.splitlines()
        for i in range(len(devlist)):
            if len(devlist[i].split(', ')) == 2 and len(devlist[i].split()) <= 7 and devlist[i].split()[1].startswith('/dev/'):
                hdinfo=devlist[i].split()
                hd=hdinfo[1].rstrip(':')
                blocks=0
                #language support
                if hdinfo[4].strip(' ').isdigit():
                    size=hdinfo[4].replace(' ','')
                else:
                    size=hdinfo[5].replace(' ','')                    
                convsize=self.convert_bytes(size)                
                rowiter=liststore.append()
                liststore.set(rowiter,0,pix,1,hd,2,blocks,3,size,4,convsize)
        print 'got hd list'        
        
    def get_partition_liststore(self):
        liststore=self.builder.get_object("partition_liststore")
        process = subprocess.Popen(['fdisk', '-l'],stdout=subprocess.PIPE,shell=False)
        outstr,err=process.communicate()
        pix=gtk.gdk.pixbuf_new_from_file(getdatapath() +'/media/drive-harddisk.svg')
        devlist=outstr.splitlines()
        for i in range(len(devlist)):
            if devlist[i].startswith(('/dev/')):
                row=devlist[i].replace('*','')
                partinfo=row.split(None,5)
                part=partinfo[0]
                blocks=partinfo[3].strip('+ ')
                size=(int(blocks) * 1024)
                convsize=self.convert_bytes(size)
                system=partinfo[5]
                rowiter=liststore.append()
                liststore.set(rowiter,0,pix,1,part,2,blocks,3,size,4,convsize,5,system)
        print 'got partition list'

    def on_i_format_combobox_changed(self, widget, data=None):
        page=self.builder.get_object("i_format_combobox").get_active_text()
        formnotebook=self.builder.get_object("i_notebook")
        self.builder.get_object("i_fwd_button").set_sensitive(False)
        if page==_("File"):
            formnotebook.set_current_page(1)
        if page==_("Harddrive"):
            formnotebook.set_current_page(2)
        if page==_("Partition"):
            formnotebook.set_current_page(3)
        
    def on_o_format_combobox_changed(self, widget, data=None):
        page=self.builder.get_object("o_format_combobox").get_active_text()
        formnotebook=self.builder.get_object("o_notebook")
        self.builder.get_object("o_fwd_button").set_sensitive(False)
        if page==_("File"):
            formnotebook.set_current_page(1)
        if page==_("Harddrive"):
            formnotebook.set_current_page(2)
        if page==_("Partition"):
            formnotebook.set_current_page(3)
            
    def on_i_filechooserwidget_changed(self, widget, data=None):
        iwidget = self.builder.get_object("i_filechooserwidget")
        i_filename = iwidget.get_filename()
        if i_filename != None :
            print i_filename, _('selected')
            self.builder.get_object("i_filechooser_path").set_label(i_filename)
            if i_filename.endswith(".tar.gz") or i_filename.endswith(".img.gz") :
                print "compressed image file found"
                self.input=[i_filename,self.get_size_from_zip(i_filename),'compressedfile',None]
            else :
                self.input=[i_filename,os.path.getsize(i_filename),'file',None]
            self.builder.get_object("i_fwd_button").set_sensitive(True)
        
    def on_o_filechooserwidget_changed(self, widget, data=None):
        owidget = self.builder.get_object("o_filechooserwidget")
        o_filename = owidget.get_filename()
        o_folder = owidget.get_current_folder()
        file_compression = self.builder.get_object("o_file_compression_check").get_active()            
        if o_filename != None and o_folder != None:
            o_filter = self.builder.get_object("o_filechooserwidget").get_filter().get_name()
            if o_filter == 'img' :
                if file_compression :
                    pre = ".img.gz"
                else:
                    pre = ".img"
            else:
                pre = ""
            if o_filename+pre != self.builder.get_object("o_filechooser_path").get_label() :
                o_filter = self.builder.get_object("o_filechooserwidget").get_filter().get_name()
                
                o_filename = o_filename + pre
                print o_filename, _('selected')            
                self.builder.get_object("o_filechooser_path").set_label(o_filename)
                s= os.statvfs(owidget.get_current_folder())
                freebytes=long(s.f_bavail * s.f_frsize)
                if file_compression :
                    self.output=[o_filename,freebytes,'compressedfile']
                else:
                    self.output=[o_filename,freebytes,'file']
                self.builder.get_object("o_fwd_button").set_sensitive(True)

    def dspaceerr_ok(self, widget, data=None):
        self.builder.get_object("space_err_messagedialog").hide()

    def on_i_fwd_button_clicked(self, widget, data=None):
        self.builder.get_object("stage_notebook").set_current_page(1)

    def on_o_back_button_clicked(self, widget, data=None):
        self.builder.get_object("stage_notebook").set_current_page(0)
        
    def on_o_fwd_button_clicked(self, widget, data=None):
        #if input and output are compressed files, do nothing, because it cannot watch 
        #for progress on dd process (why use dd for that anyway?)
        if self.input[2]=="compressedfile" and self.output[2]=="compressedfile":
            return
        #if compressed, the output size is the used Space of the Part or Disk
        if self.output[2]=="compressedfile" and self.input[2]!="file" and self.input[2]!="compressedfile":
            not_enough_space=long(self.input[4]) > long(self.output[1])
        else:
            not_enough_space=long(self.input[1]) > long(self.output[1])
        if not_enough_space:
            print _('not enough free space available')
            self.builder.get_object("space_err_messagedialog").show()
        else:
            self.builder.get_object("stage_notebook").set_current_page(2)
            self.builder.get_object("ipath_label").set_text(self.input[0])
            self.builder.get_object("opath_label").set_text(self.output[0])
        
    def on_new_button_clicked(self, widget, data=None):
        self.builder.get_object("stage_notebook").set_current_page(0)

    def on_start_dd_button_clicked(self, widget, data=None):
        self.builder.get_object("ddstart_warning_dialog").show()
        
    def start_dd_process(self, widget, response):
        if response==gtk.RESPONSE_OK:
            self.builder.get_object("ddstart_warning_dialog").hide()
            self.builder.get_object("abort_dd_button").set_sensitive(True)
            self.builder.get_object("start_dd_button").set_sensitive(False)
            self.builder.get_object("dd_back_button").set_sensitive(False)
            self.builder.get_object("new_button").set_sensitive(False)
            print 'dumping-------------'
            prefix=self.get_advanced_settings()
            if self.input[2] == "compressedfile" or self.output[2] == "compressedfile" :
                if self.input[2] == "compressedfile" :
                    firstcmd = ['gunzip', '-c', self.input[0]]
                    outputp='of='+self.output[0]
                    secondcmd = ['dd', outputp]+prefix
                    self.unzip_process = subprocess.Popen(firstcmd,
                                                          stdin=subprocess.PIPE,
                                                          stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE,
                                                          shell=False)
                    self.dd_process = subprocess.Popen(secondcmd,
                                                       stdin=self.unzip_process.stdout,
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE,
                                                       shell=False)
                else:
                    inputp='if='+self.input[0]
                    firstcmd = ['dd', inputp]+ prefix
                    secondcmd = ['gzip']
                    self.f_out = open(self.output[0], 'wb')
                    self.dd_process = subprocess.Popen(firstcmd,
                                                       stdin=subprocess.PIPE,
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE,
                                                       shell=False)
                    self.zip_process = subprocess.Popen(secondcmd,
                                                        stdin=self.dd_process.stdout,
                                                        stdout=self.f_out,
                                                        stderr=subprocess.PIPE,
                                                        shell=False)
                
            else:           
                inputp='if='+self.input[0]
                outputp='of='+self.output[0]
                command=['dd',inputp,outputp]+prefix
                self.dd_process = subprocess.Popen(command,
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE,
                                                   shell=False)

            print self.input
            print self.output

            self.timer=gobject.timeout_add(1000, self.progressbar_timeout)

        elif response==gtk.RESPONSE_CANCEL:
            self.builder.get_object("ddstart_warning_dialog").hide()

    
    def on_abort_dd_button_clicked(self, widget, data=None):
        print _('dumping aborted')
        self.dd_process.kill()
        gobject.source_remove(self.timer)
        self.builder.get_object("abort_dd_button").set_sensitive(False)
        self.builder.get_object("start_dd_button").set_sensitive(True)
        self.builder.get_object("dd_back_button").set_sensitive(True)
        self.builder.get_object("new_button").set_sensitive(True)
        
    def progressbar_timeout(self):
        isize=float(self.input[3])
        status=self.get_dd_status()
        osize=float(status[0])
        #zero division errors,because device is not ready
        if osize==0:
            osize=1
        eltime=status[2]
        if eltime==0.0:
            eltime=1.0

        remtime=int((isize-osize)/(osize/float(eltime)))
        time="EL: "+self.convert_seconds(eltime)+"/ETA: "+self.convert_seconds(abs(remtime))
        frac=(osize/isize)
        #print (osize/(isize*1.0))
        if frac <= 1.0: 
            self.builder.get_object("dd_progressbar").set_fraction(frac)
        self.builder.get_object("dd_progressbar").set_text(str(int(frac*100))+"%")
        self.builder.get_object("ddconvsize_label").set_text(status[1])
        self.builder.get_object("ddeltime_label").set_text(time)
        self.builder.get_object("ddspeed_label").set_text(status[3])
        if frac<1.0:
            return True
        else:
            self.builder.get_object("abort_dd_button").set_sensitive(False)
            #self.builder.get_object("start_dd_button").set_sensitive(True)
            self.builder.get_object("dd_back_button").set_sensitive(True)
            self.builder.get_object("new_button").set_sensitive(True)      
            self.dd_process.wait()
            if self.output[2] == "compressedfile" :
                #close File after dumping
                self.zip_process.wait()
                self.f_out.close()
            print _('dumping finished')
            if pynotify.init("gdiskdump"):
                n = pynotify.Notification ("Gdiskdump",_("The dumping Process finished succesfully."))
                try:
                    n.show()
                except:
                    print "could not show a notification"
            else:
                print "there was a problem initializing the pynotify module"
            return False
               
        
    def get_dd_status(self):
        self.dd_process.send_signal(signal.SIGUSR1)
        self.dd_process.stderr.flush()
        _ = self.dd_process.stderr.readline()
        #print self.dd_process.stderr.readline()
        self.dd_process.stderr.flush()
        _ = self.dd_process.stderr.readline()
        #print self.dd_process.stderr.readline()
        self.dd_process.stderr.flush()
        outstrr = self.dd_process.stderr.readline()
        
        #return 1 values if dd not ready
        if outstrr == "":
            print "empty string from dd process"
            return ["1","1",1,"1"]
        
        if outstrr.find('+') !=-1 :
                self.dd_process.stderr.flush()
                outstrr = self.dd_process.stderr.readline()

        print outstrr
        
        #language support
        if outstrr.find(', ') !=-1 :
            status=outstrr.split(', ')
        else:
            status=outstrr.split(',')
        sizestat=status[0].split('(')[0].split()
        sizestat[0]=sizestat[0].strip('abcdefghijklmop ')
        if sizestat[0].isdigit():
            size=sizestat[0]
        else:
            size=sizestat[1]

        convsize=self.convert_bytes(size)
        timestr=status[1].replace(',','.').split('.')[0].strip(string.letters)
        eltime=int(timestr.strip(' '))
        speed=status[2].strip('\n')
        return [size,convsize,eltime,speed]


    def get_advanced_settings(self):
        #builds the prefis for dd command
        bs=self.builder.get_object("entry_bs").get_text()
        ibs=self.builder.get_object("entry_ibs").get_text()
        obs=self.builder.get_object("entry_obs").get_text()
        count=self.builder.get_object("entry_count").get_text()
        seek=self.builder.get_object("entry_seek").get_text()
        skip=self.builder.get_object("entry_skip").get_text()
        #The size to write will change if count skip or seek is used
        #if not the size stays the same
        self.input[3]=self.input[1]

        prefix=[]        
        if ibs !="" or obs !="":
            use_ibs_obs= True
            if ibs=="":
                ibs=obs
                prefix.append('ibs='+ibs)
                prefix.append('obs='+obs)
            elif obs=="":
                obs=ibs
                prefix.append('ibs='+ibs)
                prefix.append('obs='+obs)
            else:
                prefix.append('ibs='+ibs)
                prefix.append('obs='+obs)
        elif bs !="":
            prefix.append('bs='+bs)
            use_ibs_obs= False
        if seek != "":
            prefix.append('seek='+seek)
        if skip != "":
            if use_ibs_obs==True:
                self.input[3]=int(self.input[1])-(int(skip)*int(ibs))
            else:
                self.input[3]=int(self.input[1])-(int(skip)*int(bs))
            prefix.append('skip='+skip)
        if count != "":
            if use_ibs_obs==True:
                self.input[3]=int(count)*int(ibs)
            else:
                self.input[3]=int(count)*int(bs)
            prefix.append('count='+count)
        return prefix
               
        
    def on_ipart_treeview_cursor_changed(self, widget, data=None):
        selected=self.builder.get_object("ipart_treeview").get_selection()
        model,itr=selected.get_selected()
        partition = self.builder.get_object("partition_liststore").get_value(itr,1)
        s= os.statvfs(partition)
        usedbytes=long((s.f_blocks-s.f_bfree) * s.f_frsize)
        self.input[0]=partition
        self.input[1]=self.builder.get_object("partition_liststore").get_value(itr,3)
        self.input[2]='partition'
        self.input[4]=usedbytes
        self.builder.get_object("i_fwd_button").set_sensitive(True)
        
    def on_opart_treeview_cursor_changed(self, widget, data=None):
        selected=self.builder.get_object("opart_treeview").get_selection()
        model,itr=selected.get_selected()
        self.output[0]=self.builder.get_object("partition_liststore").get_value(itr,1)
        self.output[1]=self.builder.get_object("partition_liststore").get_value(itr,3)
        self.output[2]='partition'
        self.builder.get_object("o_fwd_button").set_sensitive(True)

    def on_ihd_treeview_cursor_changed(self, widget, data=None):
        selected=self.builder.get_object("ihd_treeview").get_selection()
        model,itr=selected.get_selected()
        hd = self.builder.get_object("hd_liststore").get_value(itr,1)
        s= os.statvfs(hd)
        usedbytes=long((s.f_blocks-s.f_bfree) * s.f_frsize)
        self.input[0]=hd
        self.input[1]=self.builder.get_object("hd_liststore").get_value(itr,3)
        self.input[2]='hd'
        self.input[4]=usedbytes
        self.builder.get_object("i_fwd_button").set_sensitive(True)
        
    def on_ohd_treeview_cursor_changed(self, widget, data=None):
        selected=self.builder.get_object("ohd_treeview").get_selection()
        model,itr=selected.get_selected()
        self.output[0]=self.builder.get_object("hd_liststore").get_value(itr,1)
        self.output[1]=self.builder.get_object("hd_liststore").get_value(itr,3)
        self.output[2]='hd'
        self.builder.get_object("o_fwd_button").set_sensitive(True)
              
    def get_size_from_zip(self,path):
        fsize = 0
        imgzip=open(path, 'rb')
        #read the last 4 bytes for unconpressed file size
        imgzip.seek(-4, 2)
        fo=imgzip.read()
        imgzip.close()
        fsize=struct.unpack('<I', fo)[0]        
        print "uncompressed size %s" % (self.convert_bytes(fsize))
        return fsize


    def convert_seconds(self,seconds):
        minutes = seconds / 60
        seconds -= 60*minutes
        if minutes == 0:
            return "%02ds" % (seconds)
        else:
            return "%02dm:%02ds" % (minutes, seconds)        

    def convert_bytes(self,bytes):
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2fT' % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fG' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fM' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fK' % kilobytes
        else:
            size = '%.2fb' % bytes
        return size

    def on_dd_back_button_clicked(self, widget, data=None):
        self.builder.get_object("stage_notebook").set_current_page(1)

    def about(self, widget, data=None):
        response = self.AboutDialog.run()
        self.AboutDialog.destroy()

    def quit(self, widget, data=None):
        """quit - signal handler for closing the GdiskdumpWindow"""
        self.on_destroy(self)

    def on_destroy(self, widget, data=None):
        """on_destroy - called when the GdiskdumpWindow is close. """
        gtk.main_quit()


gdiskdumpGui = gdiskdump()
gtk.main()
