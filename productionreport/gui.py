from tkinter import *
from tkinter import filedialog, ttk

from manager import Manager


class Constants:
    NO_FILES_SELECTED = 'No Files Selected'
    NO_DIR_SELECTED = 'No Directory Selected'


class GUI:
    APP_NAME = 'Production Summarizer'
    DEFAULT_DIR = '/'

    def __init__(self, config):
        self.config = config
        self.launch()

    def launch(self):
        window = self.set_window()
        prod = ComponentGUI(window, self.config.production_dir, 'Production')
        loss = ComponentGUI(window, self.config.loss_dir, 'Loss')
        target = TargetGUI(window, self.config.target_dir)
        prod_checkbox = CheckboxGUI(window, 'Production')
        order_receipt_checkbox = CheckboxGUI(window, 'Order Receipt')
        generate = GenerateReportGUI(window, prod, loss, target, self.config, prod_checkbox, order_receipt_checkbox)
        exit_btn = ExitGUI(window)

        prod.label_static.grid(column=1, row=1, padx=15, pady=13, sticky='W')
        prod.button_browse.grid(column=4, row=1, padx=15, pady=13, sticky='EW')
        prod.label_dynamic.grid(column=1, row=2, columnspan=4, padx=15, pady=13, sticky='EW')

        ttk.Separator(window, orient='horizontal').grid(column=1, row=3, columnspan=4, sticky='ew')

        loss.label_static.grid(column=1, row=4, padx=15, pady=13, sticky='W')
        loss.button_browse.grid(column=4, row=4, padx=15, pady=13, sticky='EW')
        loss.label_dynamic.grid(column=1, row=5, columnspan=4, padx=15, pady=13, sticky='EW')

        ttk.Separator(window, orient='horizontal').grid(column=1, row=6, columnspan=4, sticky='ew')

        target.label_static.grid(column=1, row=7, padx=15, pady=13, sticky='W')
        target.button_browse.grid(column=4, row=7, padx=15, pady=13, sticky='EW')
        target.label_dynamic.grid(column=1, row=8, columnspan=4, padx=15, pady=13, sticky='EW')

        ttk.Separator(window, orient='horizontal').grid(column=1, row=9, columnspan=4, sticky='ew')

        prod_checkbox.checkbox.grid(column=2, row=10, columnspan=2, padx=15, pady=13, sticky='EW')
        order_receipt_checkbox.checkbox.grid(column=2, row=11, columnspan=2, padx=15, pady=13, sticky='EW')

        ttk.Separator(window, orient='horizontal').grid(column=1, row=12, columnspan=4, sticky='ew')

        generate.button.grid(column=2, row=13, columnspan=2, padx=15, pady=13, sticky='EW')
        exit_btn.button.grid(column=2, row=14, columnspan=2, padx=15, pady=13, sticky='EW')

        window.mainloop()

    @staticmethod
    def set_window():
        window = Tk()
        window.title(GUI.APP_NAME)
        window.config(background='azure3')
        return window


class TargetGUI:
    def __init__(self, window, destination_dir):
        self.window = window
        self.destination_dir = destination_dir
        self.label_static = self.get_label_static()
        self.label_dynamic = self.get_label_dynamic()
        self.button_browse = self.get_button_browse()

    def get_label_static(self):
        text = 'Target Directory'
        return Label(self.window, text=text, width=30, pady=7, bg='azure3')

    def get_label_dynamic(self):
        text = Constants.NO_DIR_SELECTED
        if self.destination_dir != '/':
            text = self.destination_dir
        return Label(self.window, text=text, width=70, height=4, fg='blue')

    def get_button_browse(self):
        return Button(self.window, text='Browse', width=20, command=self.browse_folder, bg='azure4', fg='white')

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.destination_dir, title='Select the target folder')
        if folder == '':
            folder = Constants.NO_DIR_SELECTED
        self.label_dynamic.configure(text=folder)


class ComponentGUI:
    def __init__(self, window, initial_dir, text):
        self.initial_dir = initial_dir
        self.text = text
        self.window = window
        self.label_static = self.get_label_static()
        self.label_dynamic = self.get_label_dynamic()
        self.button_browse = self.get_button_browse()

    def get_label_static(self):
        text = '{} Files Source Location'.format(self.text)
        return Label(self.window, text=text, width=30, pady=7, bg='azure3')

    def get_label_dynamic(self):
        return Label(self.window, text=Constants.NO_FILES_SELECTED, width=70, height=4, fg='blue')

    def get_button_browse(self):
        return Button(self.window, text='Browse', width=20, command=self.browse_files, bg='azure4', fg='white')

    def browse_files(self):
        file_types = [('Excel files', '.xlsx .xls .csv'), ('all files', '.*')]
        title = 'Select {} files'.format(self.text)
        files = filedialog.askopenfilenames(initialdir=self.initial_dir, title=title, filetypes=file_types)

        text = '\n'.join(list(files))
        if text == "":
            text = Constants.NO_FILES_SELECTED
        self.label_dynamic.configure(text=text)


class CheckboxGUI:
    def __init__(self, window, text):
        self.window = window
        self.var = IntVar()
        self.checkbox = self.get_checkbox(text)

    def get_checkbox(self, text):
        return Checkbutton(self.window, text=text, variable=self.var, bg='azure3')


class GenerateReportGUI:
    def __init__(self, window, prod_ui, loss_ui, target_ui, config, prod_checkbox, order_receipt_checkbox):
        self.config = config
        self.window = window
        self.prod_ui = prod_ui
        self.loss_ui = loss_ui
        self.target_ui = target_ui
        self.prod_checkbox = prod_checkbox
        self.order_receipt_checkbox = order_receipt_checkbox
        self.button = self.get_button()

    def get_button(self):
        return Button(self.window, text='Generate Report', bg='gray25', fg='white', width=30,
                      command=self.generate_report)

    def generate_report(self):
        prod_files = self.prod_ui.label_dynamic.cget('text')
        loss_files = self.loss_ui.label_dynamic.cget('text')
        target_dir = self.target_ui.label_dynamic.cget('text')
        production_report = self.prod_checkbox.var.get() == 1
        order_receipt_report = self.order_receipt_checkbox.var.get() == 1

        self.config.set_production_dir(prod_files)
        self.config.set_loss_dir(loss_files)
        self.config.set_target_dir(target_dir)
        self.config.write()

        prod_files_path = prod_files.split('\n')
        loss_files_path = loss_files.split('\n')

        production_columns_file_path = r'data/production_columns.csv'
        loss_state_file_path = r'data/loss_states.csv'
        ds_ts_state_file_path = r'data/ds_ts_states.csv'
        department_file_path = r'data/departments.xlsx'
        fitting_state_file_path = r'data/fitting_states.csv'
        customer_info_file_path = r'data/customer_info.csv'

        manager = Manager(prod_files_path, loss_files_path, production_columns_file_path, target_dir,
                          loss_state_file_path, ds_ts_state_file_path, department_file_path, fitting_state_file_path,
                          production_report, order_receipt_report, customer_info_file_path)
        manager.manage()


class ExitGUI:
    def __init__(self, window):
        self.window = window
        self.button = self.get_button()

    def get_button(self):
        return Button(self.window, text='EXIT', width=30, command=sys.exit)
