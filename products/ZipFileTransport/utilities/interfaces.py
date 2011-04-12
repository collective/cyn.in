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


from zope.interface import Interface

class IZipFileTransportUtility(Interface):
    """ ZipFileTransport Utility """

    def importContent(self, file, context=None, description=None, contributors=None, overwrite=0):
        """
        Import content from a zip file, creating the folder structure within a ZODB hierarchy.
        """
        
    def _checkFilePath(self, current_file, path_as_list):
        """ Make sure file isn't in a bad folder, if it is skip to the next one. """
        
    def _createFolderStructure(self, path_as_list, parent):
        """ Creates the folder structure given a path_part and parent object """

    def _logPage(self, log):
        """ Create the log page """
        
    def _createObject(self, filepath, fdata, parent):
        """
        """ 

    def _getFileObjectType(self, major, mimetype):
        """
        """        
        
    def getTime(self,id):
        """ Returns the gmtime appended to the an id, used to obtain a unique id for the logFile object """
    
    
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

    def _createObjectList(self, context, obj_paths=None):
        """
        Create a list of objects by iteratively descending a folder tree...or trees (if obj_paths is set).
        """

    def GenerateSafeFileName(self, file_name): 
        """
        Remove illegal characters from the exported filename.
        """
        
    def _getAllObjectsData(self, objects_listing, context_path):
        """ Get all of the Object """
    
    def _objImplementsInterface(self, obj, interfaceClass):
        """
        Return boolean indicating if obj implements the given interface.
        """

    def _tupleTreeToList(self, t, lsa=None):
        """Convert an instance, or tree of tuples, into list."""

    def _appendItemsToList(self, folder, list):
        """
        """

    #
    # Utility functions for use by outside tools.
    #
    #
    def getZipFilenames(self, zfile):
         """ Gets a list of filenames in the Zip archive."""
        
    def getZipFileInfo(self, zfile):
         """ Gets info about the files in a Zip archive."""
    
    def getZipFile(self, zfile, filename):
         """ Gets a file from the Zip archive."""
