import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QListWidget, QLineEdit, QCalendarWidget, 
                            QLabel, QListWidgetItem, QCheckBox, QInputDialog, QComboBox, QGridLayout)
from PyQt5.QtCore import QDate, Qt, QSize
from PyQt5.QtGui import QFont

from Sql import *

class TaskPlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Task Planner")

        Screen = QApplication.primaryScreen().availableGeometry()
        ScreenWidth, ScreenHeight = Screen.width(), Screen.height()
        WindowWidth = int(ScreenWidth * 0.8)
        WindowHeight = int(ScreenHeight * 0.8)
        self.setGeometry(
            (ScreenWidth - WindowWidth) // 2,
            (ScreenHeight - WindowHeight) // 2,
            WindowWidth,
            WindowHeight
        )
        self.showMaximized()

        self.CentralWidget = QWidget()
        self.setCentralWidget(self.CentralWidget)
        self.MainLayout = QHBoxLayout(self.CentralWidget)

        self.Sidebar = QWidget()
        self.Sidebar.setFixedWidth(150)
        SidebarLayout = QVBoxLayout(self.Sidebar)
        SidebarLayout.setAlignment(Qt.AlignTop)

        self.BtnDashboard = QPushButton("Dashboard")
        self.BtnDateTask = QPushButton("Plan Task")
        self.BtnTaskList = QPushButton("Pre Saved Task")

        self.BtnDashboard.clicked.connect(lambda: self.StackedWidget.setCurrentIndex(2))
        self.BtnDateTask.clicked.connect(lambda: self.StackedWidget.setCurrentIndex(1))
        self.BtnTaskList.clicked.connect(lambda: self.StackedWidget.setCurrentIndex(0))

        SidebarLayout.addWidget(self.BtnDashboard)
        SidebarLayout.addWidget(self.BtnDateTask)
        SidebarLayout.addWidget(self.BtnTaskList)

        self.MainLayout.addWidget(self.Sidebar)

        self.StackedWidget = QStackedWidget()
        self.MainLayout.addWidget(self.StackedWidget, 1)

        self.TaskListPage = self.CreateTaskListPage()
        self.DateTaskPage = self.CreateDateTaskPage()
        self.DashboardPage = self.CreateDashboardPage()

        self.StackedWidget.addWidget(self.TaskListPage)
        self.StackedWidget.addWidget(self.DateTaskPage)
        self.StackedWidget.addWidget(self.DashboardPage)

        self.StackedWidget.setCurrentIndex(2)

    def CreateTaskListPage(self):
        Page = QWidget()
        Layout = QVBoxLayout(Page)

        HeaderLabel = QLabel("Pre Saved Task - General Tasks")
        HeaderLabel.setFont(QFont("Arial", 16, QFont.Bold))
        HeaderLabel.setAlignment(Qt.AlignCenter)
        Layout.addWidget(HeaderLabel)
        
        self.TaskInput = QLineEdit()
        self.TaskInput.setPlaceholderText("Enter task")
        Layout.addWidget(self.TaskInput)
        
        self.TaskTypeCombo = QComboBox()
        self.TaskTypeCombo.addItems(["Daily", "Weekday Selection", "n Days Once"])
        self.TaskTypeCombo.currentIndexChanged.connect(self.UpdateTaskParamsInput)
        Layout.addWidget(QLabel("Task Type:"))
        Layout.addWidget(self.TaskTypeCombo)
        
        self.TaskParamsWidget = QWidget()
        self.TaskParamsLayout = QVBoxLayout(self.TaskParamsWidget)
        self.TaskParamsLayout.setContentsMargins(0, 0, 0, 0)
        self.WeekdayCheckboxes = {}
        self.NDaysInput = QLineEdit()
        self.NDaysInput.setPlaceholderText("Enter number of days")
        self.UpdateTaskParamsInput()
        Layout.addWidget(self.TaskParamsWidget)
        
        AddBtn = QPushButton("Add Task")
        AddBtn.clicked.connect(self.AddTask)
        Layout.addWidget(AddBtn)
        
        self.TaskList = QListWidget()
        self.TaskList.setSpacing(5)
        Layout.addWidget(self.TaskList, 1)
        
        self.LoadTasks()
        
        return Page

    def UpdateTaskParamsInput(self):
        while self.TaskParamsLayout.count():
            Item = self.TaskParamsLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
            elif Item.layout():
                while Item.layout().count():
                    SubItem = Item.layout().takeAt(0)
                    if SubItem.widget():
                        SubItem.widget().deleteLater()
        
        self.WeekdayCheckboxes = {}
        
        TaskType = self.TaskTypeCombo.currentText()
        if TaskType == "Weekday Selection":
            Weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            GridLayout = QGridLayout()
            for i, Day in enumerate(Weekdays):
                Checkbox = QCheckBox(Day)
                self.WeekdayCheckboxes[Day] = Checkbox
                GridLayout.addWidget(Checkbox, i // 4, i % 4)
            self.TaskParamsLayout.addLayout(GridLayout)
        elif TaskType == "n Days Once":
            self.TaskParamsLayout.addWidget(QLabel("Number of Days:"))
            self.TaskParamsLayout.addWidget(self.NDaysInput)
        self.TaskParamsWidget.setLayout(self.TaskParamsLayout)

    def CreateDateTaskPage(self):
        Page = QWidget()
        Layout = QVBoxLayout(Page)

        HeaderLabel = QLabel("Plan Task - Add Date-wise Task")
        HeaderLabel.setFont(QFont("Arial", 16, QFont.Bold))
        HeaderLabel.setAlignment(Qt.AlignCenter)
        Layout.addWidget(HeaderLabel)

        ContentLayout = QHBoxLayout()

        # Left: Calendar and existing tasks
        LeftWidget = QWidget()
        LeftLayout = QVBoxLayout(LeftWidget)
        self.DatePicker = QCalendarWidget()
        self.DatePicker.setFixedWidth(int(self.width() * 0.3))
        self.DatePicker.setSelectedDate(QDate.currentDate())
        self.DatePicker.selectionChanged.connect(self.UpdateDateTaskOrderList)
        LeftLayout.addWidget(self.DatePicker)
        LeftLayout.addWidget(QLabel("Select Existing Tasks:"))
        self.ExistingTaskList = QListWidget()
        self.ExistingTaskList.setSelectionMode(QListWidget.MultiSelection)
        self.ExistingTaskList.setSpacing(5)
        self.LoadExistingTasks()
        LeftLayout.addWidget(self.ExistingTaskList, 1)
        ContentLayout.addWidget(LeftWidget, 2)

        # Middle-left: Right arrow button
        MiddleLeftWidget = QWidget()
        MiddleLeftLayout = QVBoxLayout(MiddleLeftWidget)
        MiddleLeftLayout.setAlignment(Qt.AlignCenter)
        AddExistingBtn = QPushButton("→")
        AddExistingBtn.setFixedSize(40, 40)
        AddExistingBtn.clicked.connect(self.AddExistingTasks)
        MiddleLeftLayout.addWidget(AddExistingBtn)
        ContentLayout.addWidget(MiddleLeftWidget)

        # Middle: Scheduled tasks
        MiddleWidget = QWidget()
        MiddleLayout = QVBoxLayout(MiddleWidget)
        self.DateTaskInput = QLineEdit()
        self.DateTaskInput.setPlaceholderText("Enter new task for selected date")
        MiddleLayout.addWidget(self.DateTaskInput)
        AddNewTaskBtn = QPushButton("Add New Task")
        AddNewTaskBtn.clicked.connect(self.AddNewTask)
        MiddleLayout.addWidget(AddNewTaskBtn)
        MiddleLayout.addWidget(QLabel("Tasks for Selected Date (Drag to Reorder or Use Buttons):"))
        self.DateTaskOrderList = QListWidget()
        self.DateTaskOrderList.setDragDropMode(QListWidget.InternalMove)
        self.DateTaskOrderList.setSpacing(5)
        MiddleLayout.addWidget(self.DateTaskOrderList, 1)
        ContentLayout.addWidget(MiddleWidget, 3)

        # Middle-right: Left arrow button
        MiddleRightWidget = QWidget()
        MiddleRightLayout = QVBoxLayout(MiddleRightWidget)
        MiddleRightLayout.setAlignment(Qt.AlignCenter)
        AddSuggestedBtn = QPushButton("←")
        AddSuggestedBtn.setFixedSize(40, 40)
        AddSuggestedBtn.clicked.connect(self.AddSuggestedTasks)
        MiddleRightLayout.addWidget(AddSuggestedBtn)
        ContentLayout.addWidget(MiddleRightWidget)

        # Right: AI Suggested Task List
        RightWidget = QWidget()
        RightLayout = QVBoxLayout(RightWidget)
        AiHeaderLayout = QHBoxLayout()
        AiHeaderLabel = QLabel("AI Suggested Task List")
        AiHeaderLabel.setFont(QFont("Arial", 12, QFont.Bold))
        AiHeaderLayout.addWidget(AiHeaderLabel)
        RefreshBtn = QPushButton("Refresh")
        RefreshBtn.setFixedWidth(80)
        RefreshBtn.clicked.connect(self.RefreshSuggestedTasks)
        AiHeaderLayout.addWidget(RefreshBtn)
        RightLayout.addLayout(AiHeaderLayout)
        self.AiSuggestedList = QListWidget()
        self.AiSuggestedList.setSelectionMode(QListWidget.MultiSelection)
        self.AiSuggestedList.setSpacing(5)
        RightLayout.addWidget(self.AiSuggestedList, 1)
        self.RefreshSuggestedTasks()
        ContentLayout.addWidget(RightWidget, 3)

        Layout.addLayout(ContentLayout)
        self.UpdateDateTaskOrderList()

        return Page

    def CreateDashboardPage(self):
        Page = QWidget()
        Layout = QVBoxLayout(Page)

        HeaderLabel = QLabel("Dashboard - Plan Saved Task")
        HeaderLabel.setFont(QFont("Arial", 16, QFont.Bold))
        HeaderLabel.setAlignment(Qt.AlignCenter)
        Layout.addWidget(HeaderLabel)

        ContentLayout = QHBoxLayout()
        self.DashboardCalendar = QCalendarWidget()
        self.DashboardCalendar.setFixedWidth(int(self.width() * 0.3))
        self.DashboardCalendar.setSelectedDate(QDate.currentDate())
        self.DashboardCalendar.selectionChanged.connect(self.UpdateDashboard)
        ContentLayout.addWidget(self.DashboardCalendar)
        TaskWidget = QWidget()
        TaskLayout = QVBoxLayout(TaskWidget)
        self.TaskDateLabel = QLabel(f"Tasks for {QDate.currentDate().toString('MMMM d, yyyy')}")
        self.TaskDateLabel.setFont(QFont("Arial", 12))
        TaskLayout.addWidget(self.TaskDateLabel)
        self.DashboardList = QListWidget()
        self.DashboardList.setSpacing(5)
        TaskLayout.addWidget(self.DashboardList, 1)
        ContentLayout.addWidget(TaskWidget, 2)
        Layout.addLayout(ContentLayout)
        self.UpdateDashboard()
        
        return Page

    def AddTask(self):
        Task = self.TaskInput.text().strip()
        TaskType = self.TaskTypeCombo.currentText()
        TaskParams = None
        if Task:
            if TaskType == "Weekday Selection":
                SelectedDays = [Day for Day, Checkbox in self.WeekdayCheckboxes.items() if Checkbox.isChecked()]
                TaskParams = ",".join(SelectedDays) if SelectedDays else None
            elif TaskType == "n Days Once":
                TaskParams = self.NDaysInput.text().strip()
                TaskParams = TaskParams if TaskParams and TaskParams.isdigit() else None
            InsertRow("Tasks", {
                "Name": Task,
                "TaskType": TaskType,
                "TaskParams": TaskParams
            })
            self.TaskInput.clear()
            self.NDaysInput.clear()
            for Checkbox in self.WeekdayCheckboxes.values():
                Checkbox.setChecked(False)
            self.LoadTasks()
            self.LoadExistingTasks()

    def EditTask(self, TaskId):
        Tasks = GetAllRows("Tasks")
        CurrentTask = next((Task for Task in Tasks if Task["TaskId"] == TaskId), None)
        if CurrentTask:
            NewTask, Ok = QInputDialog.getText(self, "Edit Task", "Enter new task name:", QLineEdit.Normal, CurrentTask["Name"])
            if Ok and NewTask.strip():
                TaskType, OkType = QInputDialog.getItem(self, "Edit Task Type", "Select task type:", 
                                                       ["Daily", "Weekday Selection", "n Days Once"], 
                                                       ["Daily", "Weekday Selection", "n Days Once"].index(CurrentTask["TaskType"]), False)
                TaskParams = None
                if OkType:
                    if TaskType == "Weekday Selection":
                        Days, OkDays = QInputDialog.getText(self, "Edit Weekdays", 
                                                           "Enter weekdays (comma-separated, e.g., Monday,Wednesday):", 
                                                           QLineEdit.Normal, CurrentTask["TaskParams"] or "")
                        TaskParams = Days.strip() if OkDays and Days.strip() else None
                    elif TaskType == "n Days Once":
                        NDays, OkN = QInputDialog.getText(self, "Edit n Days", 
                                                         "Enter number of days:", 
                                                         QLineEdit.Normal, CurrentTask["TaskParams"] or "")
                        TaskParams = NDays.strip() if OkN and NDays.strip().isdigit() else None
                    UpdateRow("Tasks", {
                        "Name": NewTask.strip(),
                        "TaskType": TaskType,
                        "TaskParams": TaskParams,
                        "TaskId": TaskId
                    }, "TaskId")
                    Schedules = GetAllRows("TaskSchedules")
                    for Schedule in Schedules:
                        if Schedule["TaskId"] == TaskId:
                            Schedule["Name"] = NewTask.strip()
                            UpdateRow("TaskSchedules", Schedule, "ScheduleId")
                    self.LoadTasks()
                    self.LoadExistingTasks()
                    self.UpdateDateTaskOrderList()
                    self.UpdateDashboard()

    def DeleteTask(self, Date, TaskIdOrScheduleId):
        if Date is None:
            RemoveRow("Tasks", "TaskId", TaskIdOrScheduleId)
            Schedules = GetAllRows("TaskSchedules")
            for Schedule in Schedules:
                if Schedule["TaskId"] == TaskIdOrScheduleId:
                    RemoveRow("TaskSchedules", "ScheduleId", Schedule["ScheduleId"])
        else:
            RemoveRow("TaskSchedules", "ScheduleId", TaskIdOrScheduleId)
        self.LoadTasks()
        self.LoadExistingTasks()
        self.UpdateDateTaskOrderList()
        DashboardDate = self.DashboardCalendar.selectedDate().toString("yyyy-MM-dd")
        if Date is None or Date == DashboardDate:
            self.UpdateDashboard()

    def AddExistingTasks(self):
        Date = self.DatePicker.selectedDate().toString("yyyy-MM-dd")
        for Item in self.ExistingTaskList.selectedItems():
            TaskId = int(Item.data(Qt.UserRole))
            TaskName = Item.text()
            Schedules = GetAllRows("TaskSchedules")
            if not any(s for s in Schedules if s["TaskId"] == TaskId and s["Date"] == Date):
                NextOrder = max([s["OrderIndex"] for s in Schedules if s["Date"] == Date], default=-1) + 1
                InsertRow("TaskSchedules", {
                    "TaskId": TaskId,
                    "Name": TaskName,
                    "Date": Date,
                    "OrderIndex": NextOrder,
                    "Completed": 0
                })
        self.UpdateDateTaskOrderList()
        DashboardDate = self.DashboardCalendar.selectedDate().toString("yyyy-MM-dd")
        if Date == DashboardDate:
            self.UpdateDashboard()

    def AddNewTask(self):
        Date = self.DatePicker.selectedDate().toString("yyyy-MM-dd")
        Task = self.DateTaskInput.text().strip()
        if Task:
            Schedules = GetAllRows("TaskSchedules")
            NextOrder = max([s["OrderIndex"] for s in Schedules if s["Date"] == Date], default=-1) + 1
            InsertRow("TaskSchedules", {
                "TaskId": 0,
                "Name": Task,
                "Date": Date,
                "OrderIndex": NextOrder,
                "Completed": 0
            })
            self.DateTaskInput.clear()
        self.UpdateDateTaskOrderList()
        DashboardDate = self.DashboardCalendar.selectedDate().toString("yyyy-MM-dd")
        if Date == DashboardDate:
            self.UpdateDashboard()

    def AddSuggestedTasks(self):
        Date = self.DatePicker.selectedDate().toString("yyyy-MM-dd")
        for Item in self.AiSuggestedList.selectedItems():
            TaskName = Item.text()
            TaskId = Item.data(Qt.UserRole) if Item.data(Qt.UserRole) else 0
            Schedules = GetAllRows("TaskSchedules")
            if not any(s for s in Schedules if s["TaskId"] == TaskId and s["Date"] == Date and s["Name"] == TaskName):
                NextOrder = max([s["OrderIndex"] for s in Schedules if s["Date"] == Date], default=-1) + 1
                InsertRow("TaskSchedules", {
                    "TaskId": TaskId,
                    "Name": TaskName,
                    "Date": Date,
                    "OrderIndex": NextOrder,
                    "Completed": 0
                })
        self.UpdateDateTaskOrderList()
        DashboardDate = self.DashboardCalendar.selectedDate().toString("yyyy-MM-dd")
        if Date == DashboardDate:
            self.UpdateDashboard()

    def RefreshSuggestedTasks(self):
        self.AiSuggestedList.clear()
        SampleTasks = [
            {"Name": "Exercise", "TaskId": 0},
            {"Name": "Meeting", "TaskId": 0},
            {"Name": "Backup", "TaskId": 0}
        ]
        for Task in SampleTasks:
            Item = QListWidgetItem(Task["Name"])
            Item.setData(Qt.UserRole, Task["TaskId"])
            Size = QSize(0, 40)
            Item.setSizeHint(Size)
            self.AiSuggestedList.addItem(Item)

    def LoadTasks(self):
        self.TaskList.clear()
        Tasks = GetAllRows("Tasks")
        for Task in Tasks:
            Item = QListWidgetItem()
            Widget = QWidget()
            Layout = QHBoxLayout(Widget)
            
            Params = Task["TaskParams"] if Task["TaskParams"] else "None"
            Label = QLabel(f"{Task['Name']} ({Task['TaskType']}: {Params})")
            Layout.addWidget(Label, 1)
            
            EditBtn = QPushButton("Edit")
            EditBtn.setFixedWidth(50)
            EditBtn.clicked.connect(lambda _, Tid=Task["TaskId"]: self.EditTask(Tid))
            Layout.addWidget(EditBtn)
            
            DeleteBtn = QPushButton("🗑️")
            DeleteBtn.setFixedWidth(30)
            DeleteBtn.clicked.connect(lambda _, Tid=Task["TaskId"]: self.DeleteTask(None, Tid))
            Layout.addWidget(DeleteBtn)
            
            Layout.setContentsMargins(10, 5, 10, 5)
            Widget.setLayout(Layout)
            
            Size = Widget.sizeHint()
            NewSize = QSize(Size.width(), Size.height() + 20)
            Item.setSizeHint(NewSize)
            self.TaskList.addItem(Item)
            self.TaskList.setItemWidget(Item, Widget)

    def LoadExistingTasks(self):
        self.ExistingTaskList.clear()
        Tasks = GetAllRows("Tasks")
        for Task in Tasks:
            Item = QListWidgetItem(Task["Name"])
            Item.setData(Qt.UserRole, Task["TaskId"])
            Size = QSize(0, 40)
            Item.setSizeHint(Size)
            self.ExistingTaskList.addItem(Item)

    def UpdateDateTaskOrderList(self):
        self.DateTaskOrderList.clear()
        Date = self.DatePicker.selectedDate().toString("yyyy-MM-dd")
        Schedules = GetAllRows("TaskSchedules")
        DateSchedules = [s for s in Schedules if s["Date"] == Date]
        DateSchedules.sort(key=lambda x: x["OrderIndex"])
        
        for i, Schedule in enumerate(DateSchedules):
            Item = QListWidgetItem()
            Item.setData(Qt.UserRole, Schedule["ScheduleId"])
            Item.setData(Qt.UserRole + 1, Schedule["Name"])
            
            Widget = QWidget()
            Layout = QHBoxLayout(Widget)
            
            Label = QLabel(Schedule["Name"])
            Layout.addWidget(Label, 1)
            
            UpBtn = QPushButton("↑")
            UpBtn.setFixedWidth(30)
            UpBtn.clicked.connect(lambda _, Idx=i: self.MoveTaskUp(Date, Idx))
            Layout.addWidget(UpBtn)
            
            DownBtn = QPushButton("↓")
            DownBtn.setFixedWidth(30)
            DownBtn.clicked.connect(lambda _, Idx=i: self.MoveTaskDown(Date, Idx))
            Layout.addWidget(DownBtn)
            
            DeleteBtn = QPushButton("🗑️")
            DeleteBtn.setFixedWidth(30)
            DeleteBtn.clicked.connect(lambda _, Sid=Schedule["ScheduleId"]: self.DeleteTask(Date, Sid))
            Layout.addWidget(DeleteBtn)
            
            Layout.setContentsMargins(10, 5, 10, 5)
            Widget.setLayout(Layout)
            
            Size = Widget.sizeHint()
            NewSize = QSize(Size.width(), Size.height() + 20)
            Item.setSizeHint(NewSize)
            self.DateTaskOrderList.addItem(Item)
            self.DateTaskOrderList.setItemWidget(Item, Widget)
        
        self.DateTaskOrderList.model().rowsMoved.connect(self.SaveTaskOrder)

    def MoveTaskUp(self, Date, Index):
        Schedules = GetAllRows("TaskSchedules")
        DateSchedules = [s for s in Schedules if s["Date"] == Date]
        DateSchedules.sort(key=lambda x: x["OrderIndex"])
        if Index > 0:
            DateSchedules[Index]["OrderIndex"], DateSchedules[Index-1]["OrderIndex"] = \
                DateSchedules[Index-1]["OrderIndex"], DateSchedules[Index]["OrderIndex"]
            UpdateRow("TaskSchedules", DateSchedules[Index], "ScheduleId")
            UpdateRow("TaskSchedules", DateSchedules[Index-1], "ScheduleId")
            self.UpdateDateTaskOrderList()
            DashboardDate = self.DashboardCalendar.selectedDate().toString("yyyy-MM-dd")
            if Date == DashboardDate:
                self.UpdateDashboard()

    def MoveTaskDown(self, Date, Index):
        Schedules = GetAllRows("TaskSchedules")
        DateSchedules = [s for s in Schedules if s["Date"] == Date]
        DateSchedules.sort(key=lambda x: x["OrderIndex"])
        if Index < len(DateSchedules) - 1:
            DateSchedules[Index]["OrderIndex"], DateSchedules[Index+1]["OrderIndex"] = \
                DateSchedules[Index+1]["OrderIndex"], DateSchedules[Index]["OrderIndex"]
            UpdateRow("TaskSchedules", DateSchedules[Index], "ScheduleId")
            UpdateRow("TaskSchedules", DateSchedules[Index+1], "ScheduleId")
            self.UpdateDateTaskOrderList()
            DashboardDate = self.DashboardCalendar.selectedDate().toString("yyyy-MM-dd")
            if Date == DashboardDate:
                self.UpdateDashboard()

    def SaveTaskOrder(self):
        Date = self.DatePicker.selectedDate().toString("yyyy-MM-dd")
        Schedules = GetAllRows("TaskSchedules")
        DateSchedules = [s for s in Schedules if s["Date"] == Date]
        for i in range(self.DateTaskOrderList.count()):
            Item = self.DateTaskOrderList.item(i)
            ScheduleId = Item.data(Qt.UserRole)
            Schedule = next(s for s in DateSchedules if s["ScheduleId"] == ScheduleId)
            Schedule["OrderIndex"] = i
            UpdateRow("TaskSchedules", Schedule, "ScheduleId")
        self.UpdateDateTaskOrderList()
        DashboardDate = self.DashboardCalendar.selectedDate().toString("yyyy-MM-dd")
        if Date == DashboardDate:
            self.UpdateDashboard()

    def UpdateDashboard(self):
        self.DashboardList.clear()
        Date = self.DashboardCalendar.selectedDate().toString("yyyy-MM-dd")
        self.TaskDateLabel.setText(f"Tasks for {self.DashboardCalendar.selectedDate().toString('MMMM d, yyyy')}")
        Schedules = GetAllRows("TaskSchedules")
        DateSchedules = [s for s in Schedules if s["Date"] == Date]
        DateSchedules.sort(key=lambda x: x["OrderIndex"])
        
        for i, Schedule in enumerate(DateSchedules):
            Item = QListWidgetItem()
            Widget = QWidget()
            Layout = QHBoxLayout(Widget)
            
            Label = QLabel(Schedule["Name"])
            Layout.addWidget(Label, 1)
            
            Checkbox = QCheckBox()
            Checkbox.setChecked(bool(Schedule["Completed"]))
            Checkbox.stateChanged.connect(lambda State, Sid=Schedule["ScheduleId"]: self.ToggleTaskCompletion(Sid, State))
            Layout.addWidget(Checkbox)
            
            Layout.setContentsMargins(10, 5, 10, 5)
            Widget.setLayout(Layout)
            
            Size = Widget.sizeHint()
            NewSize = QSize(Size.width(), Size.height() + 20)
            Item.setSizeHint(NewSize)
            self.DashboardList.addItem(Item)
            self.DashboardList.setItemWidget(Item, Widget)

    def ToggleTaskCompletion(self, ScheduleId, State):
        Schedule = next(s for s in GetAllRows("TaskSchedules") if s["ScheduleId"] == ScheduleId)
        Schedule["Completed"] = 1 if State else 0
        UpdateRow("TaskSchedules", Schedule, "ScheduleId")
        self.UpdateDashboard()

if __name__ == '__main__':
    CreateDatabase(PersonalAssistantTom)
    Hw_Db_TableInitialization()
    App = QApplication(sys.argv)
    Window = TaskPlanner()
    Window.show()
    sys.exit(App.exec_())