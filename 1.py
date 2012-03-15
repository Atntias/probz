import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import (Application, Button, Form, CheckBox,
     FlowLayoutPanel, FlatStyle, OpenFileDialog, DialogResult, MessageBox)
from System.Drawing import Size, Rectangle

import ips, shutil

class IPSForm(Form):
    def __init__(self):
        Form.__init__(self)
        self.Text = "python-ips"
        self.ClientSize = Size(250, 70)
        self.panel = FlowLayoutPanel()
        self.backupbox = CheckBox()
        self.backupbox.Text = "Backup target"
        self.logbox = CheckBox()
        self.logbox.Text = "Save logfile"
        self.headerbox = CheckBox()
        self.headerbox.Text = "Fake header"

        button = Button()
        button.FlatStyle = FlatStyle.System
        button.Text = "Apply IPS"
        button.Click += self.patch
        self.panel.Width = 250
        self.panel.Controls.Add(self.backupbox)
        self.panel.Controls.Add(self.logbox)
        self.panel.Controls.Add(self.headerbox)
        self.panel.Controls.Add(button)
        self.Controls.Add(self.panel)

    def patch(self, x, y):
        files = True
        ipsfilter = "IPS Patch (*.IPS)|*IPS"

        pfd = OpenFileDialog(Filter = ipsfilter,
                             Title = "Select IPS Patch")
        if pfd.ShowDialog() != DialogResult.OK:
            files = False
        tfd = OpenFileDialog(Filter = "All Files (*.*)|*.*",
                             Title = "Select File to Patch")
        if tfd.ShowDialog() != DialogResult.OK:
            files = False
        if files:
            if self.backupbox.Checked:
                shutil.copyfile(tfd.FileName, tfd.FileName + ".bak")
            if ips.apply(pfd.FileName,
                         tfd.FileName,
                         self.logbox.Checked,
                         self.headerbox.Checked):
                MessageBox.Show("Successfully patched %s." % tfd.FileName,
                                "Patch Complete.")
            else:
                MessageBox.Show("Patch failed.", "Error.")

Application.EnableVisualStyles()
Application.Run(IPSForm())