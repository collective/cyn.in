##################################################################################
#    Copyright (C) 2006-2007 Utah State University, All rights reserved.          
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation; either version 2 of the License, or            
#    (at your option) any later version.                                          
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]

from Products.CMFCore.utils import UniqueObject, getToolByName
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass
from Products.CMFCore import permissions
from Products.Archetypes.atapi import *
from Products.ZipFileTransport.config import *
from Products.ATContentTypes import interfaces
from operator import itemgetter
from types import StringType
from zLOG import LOG, INFO, DEBUG
from os.path import split, splitext, splitdrive
from cStringIO import StringIO
from zipfile import ZipFile, BadZipfile, ZIP_DEFLATED
from re import compile
from urllib import unquote
from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from interfaces import IZipFileTransportUtility
from zope.event import notify
from Products.Archetypes.event import ObjectInitializedEvent

class ZipFileTransportUtility(SimpleItem):
    """ ZipFileTransport Utility """

    implements(IZipFileTransportUtility)
    
        
    # Import content to a zip file.
    #
    # file - The file input is a string of the full path name where the zip file is saved. 
    # context - Context refers to the container object where the objects will be uploaded to.
    # desc - Description is the description to be attached to the uploaded objects.
    # contributors - Contributors is the contributors message to be attached to the uploaded objects.

    def importContent(self, file, context=None, description=None, contributors=None, categories=None, overwrite=False):
        """
        Import content from a zip file, creating the folder structure within a ZODB hierarchy.
        """
        self.bad_folders = []                
 
 
        zf=ZipFile(file, 'r')
 
        files = [file.filename for file in zf.filelist]
        
        if len(files) < 1:
            return ('failure','The zip file was empty')        
        
        for current_file in files:
            
            # If the current file is a folder move to the next file.
            if current_file[-1] == '/':
                continue
            
            if current_file[0] == '/':            
                path_as_list = current_file[1:].split('/')
            else:
                path_as_list = current_file.split('/')
            
            file_name = path_as_list[-1]

            # Checks to make sure that the file path does not contain any previouslsy found bad folders.
            if not self._checkFilePath(current_file, path_as_list):
                continue
  
            folder = self._createFolderStructure(path_as_list, context)
            
            # no folder to add to? Then move on to next object.
            if not folder:
                continue

            code, msg = context.checkid(id=file_name, required=1, contained_by=folder)
            
            # Create an object if everything looks good
            if not code or (overwrite and 'existing' == code):
                
                fdata = zf.read(current_file)
                
                if "existing" ==  code:
                    folder.manage_delObjects([file_name])
 
                obj = self._createObject(file_name, fdata, folder)
                try:
                    obj.setFilename(file_name)
                except:
                    pass #do nothing
                if hasattr(obj,'description') and description:
                    obj.setDescription(description)
                if hasattr(obj,'contributors') and contributors:
                    obj.setContributors(contributors)
                if hasattr(obj,'subject') and categories:
                    obj.setSubject(categories)
                obj.reindexObject()

        zf.close()        




    def _checkFilePath(self, current_file, path_as_list):
        # Make sure file isn't in a bad folder, if it is skip to the next one.
        
        for bad_folder in self.bad_folders:
            if current_file.find(bad_folder) == 0:
                return False
        return True
        

    def _createFolderStructure(self, path_as_list, parent):
        """ Creates the folder structure given a path_part and parent object """

        props = getToolByName(self.context, 'portal_properties')
        folder_type = props.zipfile_properties.folder_type


        file_name = path_as_list[-1]

        # Create the folder structure
        for i in range( len(path_as_list) - 1 ):
            path_part = path_as_list[i]
            
            current_path = '/'.join(path_as_list[:i+1])
            
            # If not in the current folder, then just get the folder
            if path_part not in parent.objectIds():
                
                # Checks to make sure that the folder is valid.
                code, msg = parent.checkid(id=path_part, required=1, contained_by=parent)
              
                if code:
                    self.bad_folders.append(current_path)
                    return None          
                    
                parent.invokeFactory(type_name=folder_type, id=path_part)
                foldr = getattr(parent, path_part)
                foldr.setTitle(path_part)
                foldr = parent.portal_factory.doCreate(foldr, path_part)
                notify(ObjectInitializedEvent(foldr))
                self.portal_catalog.reindexObject(foldr, self.portal_catalog.indexes())
                
            else:
                foldr = getattr(parent, path_part)
                
            parent = foldr
            
        return parent
           

    def _createObject(self, filepath, fdata, parent):
        """
        """ 

        props = getToolByName(self.context, 'portal_properties')
        image_type = props.zipfile_properties.image_type
        file_type = props.zipfile_properties.file_type
        doc_type = props.zipfile_properties.doc_type
        folder_type = props.zipfile_properties.folder_type
        
        mt = parent.mimetypes_registry
        
        ext = filepath.split('.')[-1]
        ext = ext.lower()
        ftype = mt.lookupExtension(ext)    
        if ftype:
            mimetype = ftype.normalized()
            newObjType = self._getFileObjectType(ftype.major(), mimetype)        
        else:
            newObjType = self._getFileObjectType('application', 'application/octet-stream')
            mimetype = 'application/octet-stream'
        nm = filepath.split('/')
        
        if nm[-1]:
            filename = nm[-1]
        else:
            filename = nm[0]
        
        if filename not in parent.objectIds():
            parent.invokeFactory(type_name=newObjType, id=filename)
            obj = getattr(parent, filename)
            obj.setTitle(splitext(filename)[0])
                        
        else:
            obj = getattr(parent, filename)
        
        if newObjType == image_type:
            obj.setImage(fdata)
        elif newObjType == doc_type:
            obj.setText(fdata)
        elif newObjType == file_type:
            obj.setFile(fdata)

        obj = parent.portal_factory.doCreate(obj, filename)
        obj.setFormat(mimetype)
        notify(ObjectInitializedEvent(obj))
        self.portal_catalog.reindexObject(obj, self.portal_catalog.indexes())
        return obj
    

    def _getFileObjectType(self, major, mimetype):
        """
        """        
        props = getToolByName(self.context, 'portal_properties')
        image_type = props.zipfile_properties.image_type
        file_type = props.zipfile_properties.file_type
        doc_type = props.zipfile_properties.doc_type
        folder_type = props.zipfile_properties.folder_type

        if 'image' == major:
            type = image_type
        elif mimetype in ['text/html','text/plain','text/structured','text/x-rst']:
            type = doc_type            
        else:
            type = file_type
        return type
    

    def getTime(self,id):
        """ Returns the gmtime appended to the an id, used to obtain a unique id for the logFile object """
        import time
        uid = id
        for tp in time.gmtime():
            uid += str(tp)
        return uid

    #
    # Export content to a zip file.
    # 
    # context - Container refers to the container of all the objects that are to be exported.
    # obj_paths - Refers to a list of paths of either objects or contexts that will be included in the zip file.
    # filename - Refers to the fullpath filename of the exported zip file.

    def exportContent(self, context, obj_paths=None, filename=None):
        """
        Export content to a zip file.
        """      
        # create a filename without illegal characters
        objects_list = self._createObjectList(context, obj_paths)
        context_path = str( context.virtual_url_path() )
        content = self._getAllObjectsData(objects_list, context_path)
        
        return content

    def _createObjectList(self, context, obj_paths=None, state=None):
        """
        Create a list of objects by iteratively descending a folder tree...or trees (if obj_paths is set).
        """
        objects_list=[]
        
        if obj_paths:
            portal = getToolByName(self, 'portal_url', None).getPortalObject() 
            for path in obj_paths:
                obj = portal.restrictedTraverse(path)      
                #if this is a folder, then add everything in this folder to the obj_paths list otherwise simply add the object.
                if obj.isPrincipiaFolderish:
                    self._appendItemsToList(folder=obj, list=objects_list,state=state)
                elif obj not in objects_list:
                    if state:
                        if obj.portal_workflow.getInfoFor(obj,'review_state') in state:
                            objects_list.append(obj)
                    else:
                        objects_list.append(obj)
        else:
            #create a list of the objects that are contained by the context
            self._appendItemsToList(folder=context, list=objects_list,state=state)
            
        return objects_list

    def generateSafeFileName(self, file_name): 
        """
        Remove illegal characters from the exported filename.
        """
        
        # remove invalid characters from file names
        file_name = unquote(file_name)
        return file_name

    def _getAllObjectsData(self, objects_listing, context_path):
        """
        Returns the data in all files with a content object to be placed in a zipfile
        """
        # Use temporary IO object instead of writing to filesystem.
        out = StringIO()
        zipFile =  ZipFile(out, 'w', ZIP_DEFLATED)

        for obj in objects_listing:
            object_path = str(obj.virtual_url_path())
            
            if self._objImplementsInterface(obj,interfaces.IATFile) or self._objImplementsInterface(obj,interfaces.IATImage):
                file_data = str(obj.data)
                object_path = object_path.replace(context_path + '/', '')
                
            elif self._objImplementsInterface(obj,interfaces.IATDocument):

                if "text/html" == obj.Format():
                    file_data = obj.getText()
                    if object_path[-5:] != ".html" and object_path[-4:] != ".htm":                    
                        object_path += ".html"
                        
                elif "text/x-rst" == obj.Format():
                    file_data = obj.getRawText() 
                    if object_path[-4:] != ".rst":                   
                        object_path += ".rst"                    

                elif "text/structured" == obj.Format():
                    file_data = obj.getRawText() 
                    if object_path[-4:] != ".stx":                   
                        object_path += ".stx"
                        
                elif "text/plain" == obj.Format():
                    file_data = obj.getRawText() 
                    if object_path[-4:] != ".txt":                   
                        object_path += ".txt"
                        
                else:
                    file_data = obj.getRawText()

                object_path = object_path.replace(context_path + '/', '')

            elif self._objImplementsInterface(obj,interfaces.IATFolder):
                if hasattr(obj, 'getRawText'):
                    file_data = obj.getRawText()

                    if object_path == context_path:
                        object_path = object_path.split("/")[-1]
                    else:
                        object_path = object_path.replace(context_path + '/', '')
            
                    if object_path[-5:] != ".html" and object_path[-4:] != ".htm":
                        object_path += ".html"
            else:
                continue

            # start point for object path, adding 1 removes the initial '/'
            object_path = self.generateSafeFileName(object_path)
            if object_path: 
                zipFile.writestr(object_path, file_data)
                
        zipFile.close()

        out.seek(0)
        content = out.read()
        out.close()
        
        return content
    
    def _objImplementsInterface(self, obj, interfaceClass):
        """
        Return boolean indicating if obj implements the given interface.
        """
        if not hasattr(obj, '__implements__'):
            return 0
    
        if interfaceClass in self._tupleTreeToList(obj.__implements__):
            return 1
    
        return 0

    def _tupleTreeToList(self, t, lsa=None):
        """Convert an instance, or tree of tuples, into list."""
        import types
        if lsa is None: lsa = []
        if isinstance(t, types.TupleType):
            for o in t:
                self._tupleTreeToList(o, lsa)
        else:
            lsa.append(t)
        return lsa

    def _appendItemsToList(self, folder, list, state):
        """
        """
        brains = folder.portal_catalog.searchResults(path={'query':('/'.join(folder.getPhysicalPath())+'/'), })
        
        for brain_object in brains:
            obj = brain_object.getObject()
            
            if not (obj in list or obj.isPrincipiaFolderish):
                if state:
                    if obj.portal_workflow.getInfoFor(obj,'review_state') in state:
                        list.append(obj)
                else:
                    list.append(obj)
                
        return list
    


    #
    # Utility functions for use by outside tools.
    #
    #
    def getZipFilenames(self, zfile):
         """ Gets a list of filenames in the Zip archive."""
         try:
             f = ZipFile(zfile)
         except error:
             return []
         if f:
             return f.namelist()
         else:
             return []
        
    def getZipFileInfo(self, zfile):
         """ Gets info about the files in a Zip archive."""
         mt = self.mimetypes_registry
         f = ZipFile(zfile)
         fileinfo = []
         for x in f.infolist():
             fileinfo.append((x.filename, 
                              mt.lookupExtension(x.filename).normalized(), 
                              x.file_size))
         return fileinfo
    
    def getZipFile(self, zfile, filename):
         """ Gets a file from the Zip archive."""
         mt = self.mimetypes_registry
         f = ZipFile(zfile)
         finfo = f.getinfo(filename)
         fn = split(finfo.filename)[1] # Get the file name
         path = fn.replace('\\', '/')
         fp = path.split('/') # Split the file path into a list
         
         if '' == fn:
             return 'dir', fn, fp, None, None, 0, None
         ftype = mt.lookupExtension(finfo.filename)
         if not ftype:
             major = 'application'
             mimetype = 'application/octet-stream'
         else:
             major =  ftype.major()
             mimetype = ftype.normalized()
         fdata = f.read(filename)
         return 'file', fn, fp, major, mimetype, finfo.file_size, fdata


    def get_zipfile_name(self):
        return 'Test.zip'



