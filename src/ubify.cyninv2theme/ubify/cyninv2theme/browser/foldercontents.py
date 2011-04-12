from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from plone.app.content.browser.foldercontents import FolderContentsKSSView
from plone.app.content.browser.tableview import Table
from zope.app.pagetemplate import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent, aq_inner

class CyninFolderContentsView(FolderContentsView):
    """
    """
    def contents_table(self):
        table = CyninFolderContentsTable(self.context, self.request)
        return table.render()


class CyninFolderContentsTable(FolderContentsTable):
    """
    The foldercontents table renders the table and its actions.
    """

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter

        url = self.context.absolute_url()
        view_url = url + '/@@folder_contents'
        self.table = CyninTable(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)
        
    @property
    def buttons(self):
        buttons = []
        portal_actions = getToolByName(self.context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(object=aq_inner(self.context), categories=('folder_buttons', ))
        
        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.items):
            if self.context.cb_dataValid():
                for button in button_actions:
                    if button['id'] == 'paste' or button['id'] == 'import':
                        buttons.append(self.setbuttonclass(button))                    
                return buttons
            else:
                for button in button_actions:
                    if button['id'] == 'import':
                        buttons.append(self.setbuttonclass(button))
                return buttons

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] != 'paste' or self.context.cb_dataValid():
                buttons.append(self.setbuttonclass(button))
        
        return buttons

class CyninTable(Table):
    """
    The foldercontents table renders the table and its actions.
    """
    render = ViewPageTemplateFile("cynintable.pt")
    batching = ViewPageTemplateFile("cyninbatching.pt")

class CyninFolderContentsKSSView(FolderContentsKSSView):
    table = CyninFolderContentsTable
