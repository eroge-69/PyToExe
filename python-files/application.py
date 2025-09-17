#!/usr/bin/env python

import wx, file_operations, dialogs, calculations, widgets, sequencing_dialog, mutator, expression_test_calc
import auto_primer_with_save_func as auto_primer
from maker import Maker
from maker import KeyboardShortcuts

class ProDNA(wx.Frame):
    def __init__(self):
        super(ProDNA, self).__init__(None, title="ProDNA_v6.0.1: Home", size=(1190,950))
        icon = wx.Icon('linked_files/icons/dna_icon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.SetMinSize((1010,800))
        self.panel = wx.Panel(self)
        self.sizer = wx.GridBagSizer(3,4)
        self.Bind(wx.EVT_CHAR_HOOK, self.onFOne)
        self.panel.SetBackgroundColour((190,210,225))
        self.maker = Maker(self, self.panel)
        self.sequence_type= ''
        
        # shortcuts
        sc_data = [
            ['CTRL', 'Q', self.onClose],
            ['CTRL', 'F', self.onCSVSearch],
            ['CTRL', 'N', self.onNewRecord],
            ['CTRL', '<', self.collapseTree],
            ['CTRL', '>', self.expandTree]
            ]
        KeyboardShortcuts(self, data=sc_data)
        
        # toolbar
        self.toolbar = self.maker.makeToolBar(self.toolBarData())
        
        # search
        search_sizer = self.makeSearch()
        self.sizer.Add(self.search, pos=(3,0), span=(1,2),
                       flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, border=3)
        self.sizer.Add(search_sizer, pos=(3,2), flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=0)
        
        # results boxes
        self.results = widgets.ResultBoxes(self)
        self.sizer.Add(self.results.sizer, pos=(2,1), 
                       flag=wx.ALL|wx.EXPAND, border=0)

        # tree
        self.tree = widgets.ConstructTree(self.panel)
        self.tree.SetMinSize((200,-1))
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelectTree)
        self.sizer.Add(self.tree, pos=(0,0), span=(2,1), flag=wx.ALL|wx.EXPAND, border=1)
        
        # seq_box
        self.text_display = widgets.DataDisplay(self.panel, self)
        text_drop = widgets.TextDrop(self, self.text_display)
        self.text_display.SetDropTarget(text_drop)
        self.text_display.Bind(wx.EVT_LEFT_UP, self.onSelectSequence)
        self.text_display.Bind(wx.EVT_MOTION, self.onSequenceMotion)
        self.sizer.Add(self.text_display, pos=(0,1), span=(2,1), flag=wx.EXPAND|wx.ALL, border=1)
        
        # option buttons
        self.option_buttons = self.maker.makeButtons(self.optionButtonData())
        self.sizer.Add(self.option_buttons['sizer'], pos=(0,2), flag=wx.EXPAND|wx.ALL, border=1)
        
        # record buttons
        self.record_buttons = self.maker.makeButtons(self.recordButtonData(), style='horizontal')
        self.sizer.Add(self.record_buttons['sizer'], pos=(2,0), flag=wx.EXPAND|wx.ALL)
        
        # composition
        self.composition = widgets.Composition(self.panel)
        self.sizer.Add(self.composition, pos=(1,2), flag=wx.EXPAND|wx.ALL, border=1)
        
        # close button
        self.close_button = wx.Button(self.panel, label='Close')
        self.close_button.Bind(wx.EVT_BUTTON, self.onClose)
        self.sizer.Add(self.close_button, pos=(2,2), flag=wx.EXPAND|wx.ALL, border=2)
        
        #statusbar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('Press F1 for help')
        
        self.sizer.AddGrowableRow(1)
        self.sizer.AddGrowableCol(1)
        self.panel.SetSizerAndFit(self.sizer)
        self.Center()
        self.Show()
    
    def onClose(self, evt):
        a = [x for x in self.GetChildren()]
        for item in a:
            try:
                item.Destroy()
            except:
                pass
        self.DestroyChildren()
        self.Destroy()
    
    def makeSearch(self):
        self.search = wx.TextCtrl(self.panel, wx.ID_ANY, style=wx.TE_RICH2)
        self.search.Bind(wx.EVT_CHAR_HOOK, self.onSearchKey)
        search_sizer = wx.GridBagSizer(hgap=2, vgap=1)
        search_button = wx.Button(self.panel, wx.ID_ANY, label='Search')
        search_clear = wx.Button(self.panel, wx.ID_ANY, label='Clear')
        search_button.Bind(wx.EVT_BUTTON, self.onSearch)
        search_clear.Bind(wx.EVT_BUTTON, self.onSearchClear)
        search_sizer.Add(search_button, pos=(0,0), flag=wx.ALL|wx.EXPAND, border=2)
        search_sizer.Add(search_clear, pos=(0,1), flag=wx.ALL|wx.EXPAND, border=2)
        search_sizer.AddGrowableCol(0)
        search_sizer.AddGrowableCol(1)
        return search_sizer

    def onSearch(self, evt):
        term = self.search.GetValue()
        s = self.text_display.search(term)
        self.composition.Clear()
        self.composition.writeComposition(s)
    
    def onSearchClear(self, evt):
        self.search.Clear()
        self.composition.Clear()
        self.text_display.search('')
        self.tree.reselectNode()

    def onSearchKey(self, evt):
        if evt.GetKeyCode() == wx.WXK_RETURN:
            self.onSearch(evt)
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.onSearchClear(evt)
        evt.Skip()

    def optionButtonData(self):
        d = [
            ['Add/edit DNA', self.onDNA, 'D'],
            ['Add/edit protein', self.onProtein, 'D'],
            ['Add vectors', self.onVector, 'D'],
            ['Add cryostocks', self.onCryo, 'D'],
            ['Add protein_stocks', self.onProteinStock, 'D'],
            ['Add primers', self.onPrimer, 'D'],
            ['Add/edit notes', self.onNote, 'D']]
        return d
    
    def recordButtonData(self):
        d = [
            ['New', self.onNewRecord, 'D'],
            ['Delete', self.onDeleteRecord, 'D']]
        return d
    
    def toolBarData(self):
        data = [
            ['Quit', 'texit.png', self.onClose],
            ['Concentration', 'tconc.png', self.onConc],
            ['Ligate','toolbar_ligate.png', self.onLigate],
            ['Sequencing tools', 'toolbar_sequence_alignment.png', self.onSequenceAlign],
            ['DNA tools', 'toolbar_dna_tools.png', self.onDNATools],
            ['Primer tools','toolbar_primer_tools.png', self.onPrimerTools],
            ['Expression Test Calculator', 'toolbar_exp_test.png', self.onExpTest],
            ['Search stocks', 'toolbar_search.png', self.onCSVSearch]
            ]
        return data

    def onExpTest(self, evt):
        expression_test_calc.expression_GUI(self, title='Expression Test Calculator')

    def onDNATools(self, evt):
        if self.sequence_type != 'DNA':
            dialogs.messageDialog(self, 'The displayed sequence must be DNA')
        else:
            dialogs.DNATools(self, self.text_display.GetValue())
            
    def onPrimerTools(self, evt):
        #dna_prot_number_conversion.PrimerMaker(self)
        auto_primer.PrimerMaker(self)
    
    def onDesignPrimers(self, evt):
        mutator.PrimerMaker(self, seq=self.text_display.GetValue())
    
    def onCSVSearch(self, evt):
        dialogs.SearchStocks(self)
    
    def onSequenceAlign(self, evt):
        sequencing_dialog.GUI(self)
    
    def onLigate(self, evt):
        dialogs.Ligate(self)

    def onConc(self, evt):
        em = self.results.getResult('EM')
        mw = self.results.getResult('mass')
        if em != '' and mw != '':
            dialogs.ConcDialog(self, EM=em, MW=mw)
        else:
            dialogs.messageDialog(self, 'You must have a sequence displayed or selected')
    
    def onVector(self, evt):
        dialog = dialogs.CSVDialog(self, size=(500,100),
                                       title='Add a new vector...')
        dialog.layout('VECTORS', self.fasta_id)
        if dialog.ShowModal() == wx.ID_OK:
            dialog.writeData()
            self.tree.reselectNode()
        dialog.Destroy()

    def onCryo(self, evt):
        dialog = dialogs.CSVDialog(self, size=(500,100),
                                       title='Add a new cryostock...')
        dialog.layout('CRYOSTOCKS', self.fasta_id)
        if dialog.ShowModal() == wx.ID_OK:
            dialog.writeData()
            self.tree.reselectNode()
        dialog.Destroy()
    
    def onPrimer(self, evt):
        dialog = dialogs.CSVDialog(self, size=(400,295),
                                       title='Add a new primer...')
        dialog.layout('PRIMERS', self.fasta_id)
        if dialog.ShowModal() == wx.ID_OK:
            dialog.writeData()
            self.tree.reselectNode()
        dialog.Destroy()
    
    def onProteinStock(self, evt):
        dialog = dialogs.CSVDialog(self, size=(400,295),
                                       title='Add a new protein stock...')
        dialog.layout('PROTEIN_STOCKS', self.fasta_id)
        if dialog.ShowModal() == wx.ID_OK:
            dialog.writeData()
            self.tree.reselectNode()
        dialog.Destroy()
    
    def onNote(self, evt):
        dialog = dialogs.NoteDialog(self, title='Add/edit note...')
        dialog.layout(self.fasta_id)
        if dialog.ShowModal() == wx.ID_OK:
            dialog.writeData()
            self.tree.reselectNode()
        dialog.Destroy()

    def onDNA(self, evt):
        dialog = dialogs.FastaDialog(self, title='Add/edit DNA sequence...')
        dialog.layout('DNA', self.fasta_id)
        if dialog.ShowModal() == wx.ID_OK:
            dialog.writeData()
            self.tree.reselectNode()
        dialog.Destroy()

    def onProtein(self, evt):
        dialog = dialogs.FastaDialog(self, title='Add/edit protein sequence...')
        dialog.layout('PROTEIN', self.fasta_id)
        if dialog.ShowModal() == wx.ID_OK:
            dialog.writeData()
            self.tree.reselectNode()
        dialog.Destroy()
    
    def onNewRecord(self, evt):
        try:
            if len(self.node_path) == 1:
                family = ''
            else:
                family = self.node_path[1]
            construct = ''
            dialog = dialogs.MasterRecordDialog(self, title='Add new record...')
            dialog.layout(family, construct)
            if dialog.ShowModal() == wx.ID_OK:
                dialog.writeData()
                self.tree.populateTree()
            dialog.Destroy()
        except: pass
    
    def onDeleteRecord(self, evt):
        dialog = wx.MessageDialog(self, 'Are you sure you want to delete this record?','Question',
                                  wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if dialog.ShowModal() == wx.ID_YES:
            file_operations.FileWorker().deleteMasterRecord(self.node_path[1],self.node_path[2])
            self.tree.populateTree()
        dialog.Destroy()
    
    def alterOptionButtonState(self):
        keys = [k for k in self.option_buttons.keys() if k != 'sizer']
        for key in keys:
            
            if self.sequence_type == key.split(' ')[-1] or self.sequence_type.lower() == key.split(' ')[-1]:
                self.option_buttons[key].Enable()
            else:
                self.option_buttons[key].Disable()
        if len(self.node_path) == 1:
            self.record_buttons['New'].Enable()
            self.record_buttons['Delete'].Disable()
        elif len(self.node_path) == 2:
            self.record_buttons['New'].Enable()
            self.record_buttons['Delete'].Disable()
        elif len(self.node_path) == 3:
            self.record_buttons['New'].Disable()
            self.record_buttons['Delete'].Enable()
        elif len(self.node_path) == 4:
            self.record_buttons['New'].Disable()
            self.record_buttons['Delete'].Disable()

    def onSelectTree(self, evt):
        self.text_display.Clear()
        self.composition.Clear()
        self.results.clearResults()
        self.statusbar.SetStatusText('Press F1 for help')
        self.sequence_type = ''
        operations = file_operations.FileWorker()
        selected = evt.GetItem()
        self.node_path = self.tree.getNodePath(selected)
        if len(self.node_path) == 4:
            fam, con, option = self.node_path[1:]
            self.sequence_type = option
            self.fasta_id = '_'.join(fam.split(' ')) + '_' + '_'.join(con.split(' '))
            try:
                if fam == 'drag_and_drop':
                    data = operations.openDroppedFile(con)
                    if option == 'DNA':
                        self.text_display.writeText(data, text_style='sequence')
                        self.setResults(data, 'DNA')
                    elif option == 'PROTEIN':
                        self.text_display.writeText(data, text_style='sequence')
                        self.setResults(data)
                elif option in file_operations.linked_csv.keys():
                    data = operations.getCSVByFastaID(option, self.fasta_id)
                    t = self.displayCSV(data)
                    self.text_display.writeText(t)
                elif option in file_operations.linked_fasta.keys():
                    data = operations.getFastaByID(option, self.fasta_id)
                    if option == 'DNA':
                        self.text_display.writeText(data, text_style='sequence')
                        self.setResults(data, 'DNA')
                    elif option == 'PROTEIN':
                        self.text_display.writeText(data, text_style='sequence')
                        self.setResults(data)
                    elif option == 'NOTES':
                        data = operations.getNoteByID(self.fasta_id)
                        self.text_display.writeText(data)
            except: pass
        self.alterOptionButtonState()
    
    def setResults(self, sequence, sequence_type='PROTEIN'):
        results = calculations.SequenceManipulation().calcSeq(sequence, sequence_type)
        self.composition.Clear()
        self.results.clearResults()
        self.results.setResults(results)
        self.composition.writeComposition(results['count'])
    
    def onSelectSequence(self, evt):
        self.statusbar.SetStatusText('Press F1 for help')
        sequence = self.text_display.GetValue()
        a,b = self.text_display.GetSelection()
        self.results.clearResults()
        if a != b:
            selected = sequence[a:b]
            a += 1
            if b >= len(sequence): b = len(sequence)
            if self.sequence_type == 'PROTEIN':
                status_text = 'selected: ' + str(a) + ' to ' + str(b)
                self.setResults(selected)
                self.statusbar.SetStatusText(status_text)
            elif self.sequence_type == 'DNA':
                status_text = 'selected: ' + str(a) + ' to ' + str(b)
                self.setResults(selected, 'DNA')
                self.statusbar.SetStatusText(status_text)
            elif self.sequence_type == 'PRIMERS':
                try:
                    self.setResults(selected.strip(' \n'), 'DNA')
                except: pass
        elif a == b:
            a += 1
            if a >= len(sequence): a = len(sequence)
            if self.sequence_type == 'PROTEIN':
                status_text = 'sequence position: ' + str(a)
                self.setResults(sequence)
            elif self.sequence_type == 'DNA':
                status_text = 'sequence position: ' + str(a)
                self.setResults(sequence, 'DNA')
            elif self.sequence_type == 'PRIMERS':
                try:
                    self.setResults(sequence, 'DNA')
                except: pass
            try:
                self.statusbar.SetStatusText(status_text)
            except: pass
        evt.Skip()
    
    def onSequenceMotion(self, evt):
        if evt.LeftIsDown() and evt.Dragging():
            seq = self.text_display.GetValue()
            a,b = self.text_display.GetSelection()
            if a == 0: a+=1
            if b == 0: b+=1
            if a > len(seq): a = len(seq)
            if b > len(seq): b = len(seq)
            s = str(a) + ' .. ' + str(b)
            self.statusbar.SetStatusText(s)
        evt.Skip()
    
    def displayCSV(self, data, pad=3):
        headers = data.pop(0)
        cols = {}
        for i,h in enumerate(headers):
            cols[i] = [h]
        for dic in data:
            for i,h in enumerate(headers):
                cols[i].append(dic[h])
        col_widths = []
        col_no = cols.keys()
        col_no.sort()
        for n in col_no:
            col = cols[n]
            c = sorted(col, key=len)
            max_w = len(c[-1]) + pad
            col_widths.append(max_w)
        rows = len(cols[0])
        text = ''
        for i in range(rows):
            for n in col_no:
                w = col_widths[n]
                v = cols[n][i]
                v += ' '*(w-len(v))
                text += v
            text += '\n'
        return text
    
    def onFOne(self, evt):
        keycode = evt.GetKeyCode()
        if keycode == wx.WXK_F1:
            dialogs.AboutDialog(self)
        else:
            evt.Skip()

    def collapseTree(self, evt):
        root = self.tree.GetRootItem()
        sel = self.tree.GetSelection()
        try:
            self.tree.CollapseAllChildren(sel)
        except:
            self.tree.CollapseAll()
            self.tree.Expand(root)
    
    def expandTree(self, evt):
        sel = self.tree.GetSelection()
        try:
            self.tree.ExpandAllChildren(sel)
        except:
            self.tree.ExpandAll()


if __name__ == "__main__":
    app = wx.App()
    frame = ProDNA()
    app.MainLoop()