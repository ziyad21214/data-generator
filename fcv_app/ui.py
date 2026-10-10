"""
wxPython user interface implementation for the Faker CSV Generator.
"""

import os
import wx
import threading
from typing import List
from .models import ColumnDefinition, GenerationConfig
from .generator import CSVGeneratorEngine


class ColumnEditorDialog(wx.Dialog):
    POPULAR_PROVIDERS = [
        "name", "first_name", "last_name", "email", "phone_number",
        "address", "city", "country", "postalcode", "company",
        "job", "date", "ipv4", "url", "text", "uuid4"
    ]

    def __init__(self, parent, column_name="", provider_name="name"):
        super().__init__(parent, title="Configure Column", size=(400, 250))
        
        self.column_name = column_name
        self.provider_name = provider_name
        
        self._init_ui()

    def _init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(wx.StaticText(panel, label="Column Name:"), 0, wx.ALL | wx.TOP, 10)
        self.name_ctrl = wx.TextCtrl(panel, value=self.column_name)
        sizer.Add(self.name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        sizer.Add(wx.StaticText(panel, label="Faker Provider (e.g., name, address, email):"), 0, wx.ALL | wx.TOP, 10)
        self.provider_ctrl = wx.ComboBox(panel, value=self.provider_name, choices=self.POPULAR_PROVIDERS, style=wx.CB_DROPDOWN)
        sizer.Add(self.provider_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        btn_sizer = wx.StdDialogButtonSizer()
        
        save_btn = wx.Button(panel, wx.ID_OK, label="Save")
        save_btn.SetDefault()
        btn_sizer.AddButton(save_btn)
        
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, label="Cancel")
        btn_sizer.AddButton(cancel_btn)
        
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)

        panel.SetSizer(sizer)
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        self.column_name = self.name_ctrl.GetValue().strip()
        self.provider_name = self.provider_ctrl.GetValue().strip()

        if not self.column_name or not self.provider_name:
            wx.MessageBox("Both Column Name and Faker Provider are required.", "Validation Error", wx.OK | wx.ICON_ERROR)
            return

        self.EndModal(wx.ID_OK)

    def get_column_definition(self) -> ColumnDefinition:
        return ColumnDefinition(name=self.column_name, faker_provider=self.provider_name)


class MainFrame(wx.Frame):
    LOCALES = ["en_US", "en_GB", "fr_FR", "de_DE", "es_ES", "it_IT", "ja_JP", "ar_AA"]

    def __init__(self):
        super().__init__(None, title="Fake Data Generator", size=(700, 600))
        self.columns: List[ColumnDefinition] = [
            ColumnDefinition("ID", "uuid4"),
            ColumnDefinition("Full Name", "name"),
            ColumnDefinition("Email", "email"),
            ColumnDefinition("Company", "company")
        ]
        self._init_ui()
        self.Center()
        self.SetIcon(wx.Icon("resources/icon.ico", wx.BITMAP_TYPE_ICO))  
    def _init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        settings_box = wx.StaticBox(panel, label="Generation Settings")
        settings_sizer = wx.StaticBoxSizer(settings_box, wx.VERTICAL)

        grid_sizer = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=10)
        grid_sizer.AddGrowableCol(1, 1)

        grid_sizer.Add(wx.StaticText(panel, label="Number of Rows:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.rows_spin = wx.SpinCtrl(panel, value="100", min=1, max=10000000)
        grid_sizer.Add(self.rows_spin, 0, wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Faker Locale:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.locale_combo = wx.ComboBox(panel, choices=self.LOCALES, value="en_US", style=wx.CB_READONLY)
        grid_sizer.Add(self.locale_combo, 0, wx.EXPAND)

        grid_sizer.Add(wx.StaticText(panel, label="Output CSV File:"), 0, wx.ALIGN_CENTER_VERTICAL)
        file_picker_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.path_ctrl = wx.TextCtrl(panel, value=os.path.abspath("generated_data.csv"))
        file_picker_sizer.Add(self.path_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        browse_btn = wx.Button(panel, label="Browse...")
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        file_picker_sizer.Add(browse_btn, 0)
        grid_sizer.Add(file_picker_sizer, 0, wx.EXPAND)

        settings_sizer.Add(grid_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(settings_sizer, 0, wx.EXPAND | wx.ALL, 10)

        cols_box = wx.StaticBox(panel, label="Columns Configuration")
        cols_sizer = wx.StaticBoxSizer(cols_box, wx.VERTICAL)

        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        self.list_ctrl.AppendColumn("Column Name", width=250)
        self.list_ctrl.AppendColumn("Faker Provider", width=300)
        self._refresh_column_list()
        cols_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        btn_hb_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_btn = wx.Button(panel, label="Add Column")
        edit_btn = wx.Button(panel, label="Edit Column")
        del_btn = wx.Button(panel, label="Remove Column")
        
        add_btn.Bind(wx.EVT_BUTTON, self.on_add_column)
        edit_btn.Bind(wx.EVT_BUTTON, self.on_edit_column)
        del_btn.Bind(wx.EVT_BUTTON, self.on_remove_column)

        btn_hb_sizer.Add(add_btn, 0, wx.RIGHT, 5)
        btn_hb_sizer.Add(edit_btn, 0, wx.RIGHT, 5)
        btn_hb_sizer.Add(del_btn, 0)
        cols_sizer.Add(btn_hb_sizer, 0, wx.ALL, 5)

        main_sizer.Add(cols_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.progress_bar = wx.Gauge(panel, range=100)
        bottom_sizer.Add(self.progress_bar, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        self.generate_btn = wx.Button(panel, label="Generate CSV", size=(140, 35))
        self.generate_btn.SetBackgroundColour(wx.Colour(40, 167, 69))
        self.generate_btn.SetForegroundColour(wx.WHITE)
        self.generate_btn.Bind(wx.EVT_BUTTON, self.on_generate)
        bottom_sizer.Add(self.generate_btn, 0)

        main_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        panel.SetSizer(main_sizer)

    def _refresh_column_list(self):
        self.list_ctrl.DeleteAllItems()
        for idx, col in enumerate(self.columns):
            self.list_ctrl.InsertItem(idx, col.name)
            self.list_ctrl.SetItem(idx, 1, col.faker_provider)

    def on_browse(self, event):
        dialog = wx.FileDialog(
            self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )
        if dialog.ShowModal() == wx.ID_OK:
            self.path_ctrl.SetValue(dialog.GetPath())
        dialog.Destroy()

    def on_add_column(self, event):
        dialog = ColumnEditorDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            self.columns.append(dialog.get_column_definition())
            self._refresh_column_list()
        dialog.Destroy()

    def on_edit_column(self, event):
        selected = self.list_ctrl.GetFirstSelected()
        if selected == -1:
            wx.MessageBox("Please select a column to edit.", "Selection Required", wx.OK | wx.ICON_WARNING)
            return

        col = self.columns[selected]
        dialog = ColumnEditorDialog(self, column_name=col.name, provider_name=col.faker_provider)
        if dialog.ShowModal() == wx.ID_OK:
            self.columns[selected] = dialog.get_column_definition()
            self._refresh_column_list()
        dialog.Destroy()

    def on_remove_column(self, event):
        selected = self.list_ctrl.GetFirstSelected()
        if selected == -1:
            wx.MessageBox("Please select a column to remove.", "Selection Required", wx.OK | wx.ICON_WARNING)
            return

        del self.columns[selected]
        self._refresh_column_list()

    def on_generate(self, event):
        row_count = self.rows_spin.GetValue()
        file_path = self.path_ctrl.GetValue().strip()
        locale = self.locale_combo.GetValue()

        if not file_path:
            wx.MessageBox("Please specify a valid output file path.", "Error", wx.OK | wx.ICON_ERROR)
            return

        if not self.columns:
            wx.MessageBox("Please add at least one column definition.", "Error", wx.OK | wx.ICON_ERROR)
            return

        config = GenerationConfig(
            row_count=row_count,
            file_path=file_path,
            locale=locale,
            columns=self.columns
        )

        self.generate_btn.Disable()
        self.progress_bar.SetValue(0)

        threading.Thread(target=self._run_generation_task, args=(config,), daemon=True).start()

    def _run_generation_task(self, config: GenerationConfig):
        try:
            engine = CSVGeneratorEngine(config)

            def progress_callback(current, total):
                percentage = int((current / total) * 100)
                wx.CallAfter(self.progress_bar.SetValue, percentage)

            engine.generate(progress_callback=progress_callback)

            wx.CallAfter(self._on_generation_success, config.file_path)
        except Exception as e:
            wx.CallAfter(self._on_generation_error, str(e))

    def _on_generation_success(self, file_path: str):
        self.generate_btn.Enable()
        self.progress_bar.SetValue(100)
        wx.MessageBox(f"CSV successfully generated!\nSaved to: {file_path}", "Success", wx.OK | wx.ICON_INFORMATION)

    def _on_generation_error(self, err_msg: str):
        self.generate_btn.Enable()
        self.progress_bar.SetValue(0)
        wx.MessageBox(f"Failed to generate CSV:\n{err_msg}", "Error", wx.OK | wx.ICON_ERROR)