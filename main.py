import datetime
import csv
import os
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.pickers import MDTimePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp

Window.size = (412,870)

script_directory = os.path.dirname(os.path.realpath(__file__))
filename = 'records.csv'
csv_file_path = os.path.join(script_directory, filename)

G_categories = []
G_sources = ["HDFC Bank", "PayTm Bank", "Cash", "IDFC Credit Card", "HDFC Credit Card", "SC Credit Card"]
G_Record = {
    "type": "",
    "category": "",
    "name": "",
    "description": "",
    "source": "",
    "amount": "",
    "datetime": ""
}


def G_updateCategories():
    catlist=[]
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as csvfile:
            for line in csv.DictReader(csvfile):
                catlist.append(line["category"])
    global G_categories
    G_categories = catlist

def G_addToCSV(data):

    with open(csv_file_path, 'a', newline='') as csvfile:
        fieldnames = data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow(data)
    return True

class categorydialog(BoxLayout):
    pass

class Demo(MDScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids["dateTimeLabel_id"].text = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        G_updateCategories()

    def saveTransaction(self):
        if G_Record["type"] == "":
            G_Record["type"] = "Expense"
        G_Record["name"] = self.ids["nameInput_id"].text
        G_Record["description"] = self.ids["descriptionInput_id"].text
        G_Record["amount"] = self.ids["amountInput_id"].text
        G_Record["datetime"] = self.ids["dateTimeLabel_id"].text

        if self.validateSave() == True:
            result = G_addToCSV(G_Record)
            if result:
                self.updateLogText()
                G_updateCategories()
                Snackbar(text="Transaction Saved").open()
    def validateSave(self):
        if G_Record["type"] == "":
            # print("type null error")
            Snackbar(text="Choose a type first").open()
            return False
        if G_Record["category"] == "":
            # print("category null error")
            Snackbar(text="Select or Create a Category First").open()
            return False
        if G_Record["source"] == "":
            # print("source null error")
            Snackbar(text="Select a source first").open()
            return False
        if G_Record["datetime"] == "":
            # print("datetime null error")
            Snackbar(text="Choose proper datetime").open()
            return False
        if G_Record["amount"].replace('.','',1).isdigit() == False:
            # print("amount invalid error")
            Snackbar(text="Amount not entered or invalid").open()
            return False
        return True
    def typeButtonPressed(self,id):

        if id == "expenseBtn_id":
            G_Record["type"] = "Expense"
            btn_en = self.ids["expenseBtn_id"]
            btn_dis = self.ids["incomeBtn_id"]
        if id == "incomeBtn_id":
            G_Record["type"] = "Income"
            btn_en = self.ids["incomeBtn_id"]
            btn_dis = self.ids["expenseBtn_id"]

        btn_en.line_color = get_color_from_hex("#3b719f")
        btn_en.text_color = get_color_from_hex("#ffffff")
        btn_en.md_bg_color = get_color_from_hex("#3b719f")
        btn_dis.line_color = get_color_from_hex("#000000")
        btn_dis.text_color = get_color_from_hex("#000000")
        btn_dis.md_bg_color = get_color_from_hex("#bebebe")
    def menupressed(self,txt,dtype):
        print(txt)
        if dtype == "category":
            self.ids["selectCategoryBtn_id"].text = txt
            G_Record["category"] = txt
            self.catmenu.dismiss()
        if dtype == "source":
            self.ids["selectSourceBtn_id"].text = txt
            G_Record["source"] = txt
            self.sourcemenu.dismiss()
    def categoryDropdown(self):
        categoryMenuList = []
        for cat in G_categories:
            tmp={
                "viewclass": "OneLineListItem",
                "text": cat,
                "on_release": lambda x=cat: self.menupressed(x,"category")
            }
            categoryMenuList.append(tmp)

        self.catmenu = MDDropdownMenu(

            caller = self.ids["selectCategoryBtn_id"],
            items = categoryMenuList,
            width_mult = 4
        )
        self.catmenu.open()
    def sourceDropdown(self):
        sourceMenuList = []
        for name in G_sources:
            tmp={
                "viewclass": "OneLineListItem",
                "text": name,
                "on_release": lambda x=name: self.menupressed(x,"source")
            }
            sourceMenuList.append(tmp)

        self.sourcemenu = MDDropdownMenu(
            caller = self.ids["selectSourceBtn_id"],
            items = sourceMenuList,
            width_mult = 4
        )
        self.sourcemenu.open()
    def choose_date(self):
        add_txn_datePicker = MDDatePicker()
        add_txn_datePicker.bind(on_save=self.get_date)
        add_txn_datePicker.open()
    def get_date(self, instance, value, date_range):
        self.add_txn_date = value
        add_txn_timePicker = MDTimePicker()
        add_txn_timePicker.bind(on_save=self.get_time)
        add_txn_timePicker.open()
    def get_time(self, instance, value):
        self.add_txn_time = value
        self.save_txn_datetime()
    def save_txn_datetime(self):
        dateTimeText = str(self.add_txn_date) + ' ' + str(self.add_txn_time)
        a = str(datetime.datetime.strptime(dateTimeText, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M"))
        txn_date = self.ids['dateTimeLabel_id']
        txn_date.text = a
        # G_Record["datetime"] = a
        # print(a)
    def createCategoryDialog(self):

        categorydialogContent = categorydialog()
        self.dialog = MDDialog(title="Create Category", type="custom", content_cls=categorydialogContent,
                               buttons=[
                                   MDFlatButton(
                                       text="CANCEL",
                                       on_release=lambda x: self.saveCreatedCategory("na")

                                   ),
                                   MDFlatButton(
                                       text="SAVE",
                                       on_release = lambda x: self.saveCreatedCategory(categorydialogContent.ids["createCategoryTextField_id"].text)
                                   ),
                               ],
                               )

        self.dialog.open()
    def saveCreatedCategory(self,txt):
        if txt == "na":
            self.dialog.dismiss()
        elif txt == "":
            # print("Enter a name first")
            Snackbar(text = "Enter a name first").open()
        else:
            self.ids["selectCategoryBtn_id"].text = txt
            G_Record["category"] = txt
            self.dialog.dismiss()
    def exportConfirm(self,ins):
        snackbar = Snackbar(
            text="Export Transactions as CSV File?",
            duration=10
        )

        snackbar.buttons = [
            MDRectangleFlatButton(
                text="No",
                line_width= 1.2,
                line_color=get_color_from_hex("#ffffff"),
                text_color=get_color_from_hex("#ffffff"),
                on_release=snackbar.dismiss,
            ),
            MDRectangleFlatButton(
                text="Yes",
                line_width=1.2,
                line_color=get_color_from_hex("#ffffff"),
                text_color=get_color_from_hex("#ffffff"),
                on_release=self.exportCSV,
                on_press=snackbar.dismiss
            )
        ]
        snackbar.open()

    def exportCSV(self,ins):
        print("ok")

    def viewCSV(self,ins):
        card = self.ids["viewTxnCard_id"]

        # a.opacity = 1 if a.opacity == 0 else 0
        if card.opacity == 0:
            self.updateLogText()
            card.opacity = 1
        else:
            card.opacity = 0

    def updateLogText(self):

        finaltxt = ""
        self.pagedTxt=[]
        with open(csv_file_path, 'r', newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            count = 1
            rownum = 0
            # page=1
            for row in csvreader:
                if count>25:
                    self.pagedTxt.append(finaltxt)
                    finaltxt=""
                    count=0

                txt = ", ".join(row)
                finaltxt = finaltxt + '{' +str(rownum)+', '+ txt + '}\n'
                rownum += 1
                count +=1
            self.pagedTxt.append(finaltxt)

        self.pageNum = len(self.pagedTxt)
        self.changePage("same")

    def changePage(self,val):
        if val == "inc" and self.pageNum < len(self.pagedTxt):
            self.pageNum += 1
        if val == "dec" and self.pageNum > 1:
            self.pageNum -= 1

        label = self.ids["logbox_id"]
        pagelabel = self.ids["pagelabel_id"]
        pagelabel.text = str(self.pageNum)
        label.text = str(self.pagedTxt[self.pageNum - 1])
        print(val)

    def deleteRecord(self):
        print("gghdh")
        num = self.ids["deleteRecordRow_id"].text
        if not num.isdigit():
            Snackbar(text="Invalid Row Number").open()
            return
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        if int(num) >= len(rows):
            Snackbar(text="Invalid Row Number").open()
            return

        rows.pop(int(num))
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # writer.writerow(["type","category","name","description","source","amount","datetime"])
            writer.writerows(rows)
            self.ids["deleteRecordRow_id"].text = ""
            Snackbar(text="Deleted").open()

        return

class Temp(MDApp):
    def build(self):
        script_directory = os.path.dirname(os.path.realpath(__file__))
        filename = 'templayout.kv'
        kv_file_path = os.path.join(script_directory, filename)
        Builder.load_file(kv_file_path)
        print(self.user_data_dir)
        sl = Demo()
        return sl

if __name__ == '__main__':
    Temp().run()