import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QListWidget, QLineEdit, QCalendarWidget, 
                            QLabel, QListWidgetItem, QCheckBox, QInputDialog)
from PyQt5.QtCore import QDate, Qt, QSize
from PyQt5.QtGui import QFont

from Sql import *

class TaskPlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Task Planner")

        screen = QApplication.primaryScreen().availableGeometry()
        screen_width, screen_height = screen.width(), screen.height()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.setGeometry(
            (screen_width - window_width) // 2,
            (screen_height - window_height) // 2,
            window_width,
            window_height
        )
        self.showMaximized()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(150)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_date_task = QPushButton("Plan Task")
        self.btn_task_list = QPushButton("Pre Saved Task")

        self.btn_dashboard.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.btn_date_task.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_task_list.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_date_task)
        sidebar_layout.addWidget(self.btn_task_list)

        self.main_layout.addWidget(self.sidebar)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget, 1)

        self.task_list_page = self.create_task_list_page()
        self.date_task_page = self.create_date_task_page()
        self.dashboard_page = self.create_dashboard_page()

        self.stacked_widget.addWidget(self.task_list_page)
        self.stacked_widget.addWidget(self.date_task_page)
        self.stacked_widget.addWidget(self.dashboard_page)

        self.stacked_widget.setCurrentIndex(2)

    def create_task_list_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        header_label = QLabel("Pre Saved Task - General Tasks")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task")
        layout.addWidget(self.task_input)
        
        add_btn = QPushButton("Add Task")
        add_btn.clicked.connect(self.add_task)
        layout.addWidget(add_btn)
        
        self.task_list = QListWidget()
        self.task_list.setSpacing(5)
        layout.addWidget(self.task_list, 1)
        
        self.load_tasks()
        
        return page

    def create_date_task_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        header_label = QLabel("Plan Task - Add Date-wise Task")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        content_layout = QHBoxLayout()

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.date_picker = QCalendarWidget()
        self.date_picker.setFixedWidth(int(self.width() * 0.3))
        self.date_picker.setSelectedDate(QDate.currentDate())
        self.date_picker.selectionChanged.connect(self.update_date_task_order_list)
        left_layout.addWidget(self.date_picker)

        left_layout.addWidget(QLabel("Select Existing Tasks:"))
        self.existing_task_list = QListWidget()
        self.existing_task_list.setSelectionMode(QListWidget.MultiSelection)
        self.existing_task_list.setSpacing(5)
        self.load_existing_tasks()
        left_layout.addWidget(self.existing_task_list, 1)

        content_layout.addWidget(left_widget)

        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setAlignment(Qt.AlignCenter)
        add_existing_btn = QPushButton("→")
        add_existing_btn.setFixedSize(40, 40)
        add_existing_btn.clicked.connect(self.add_existing_tasks)
        middle_layout.addWidget(add_existing_btn)
        content_layout.addWidget(middle_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.date_task_input = QLineEdit()
        self.date_task_input.setPlaceholderText("Enter new task for selected date")
        right_layout.addWidget(self.date_task_input)

        add_new_task_btn = QPushButton("Add New Task")
        add_new_task_btn.clicked.connect(self.add_new_task)
        right_layout.addWidget(add_new_task_btn)

        right_layout.addWidget(QLabel("Tasks for Selected Date (Drag to Reorder or Use Buttons):"))
        self.date_task_order_list = QListWidget()
        self.date_task_order_list.setDragDropMode(QListWidget.InternalMove)
        self.date_task_order_list.setSpacing(5)
        right_layout.addWidget(self.date_task_order_list, 1)

        content_layout.addWidget(right_widget, 2)
        layout.addLayout(content_layout)

        self.update_date_task_order_list()

        return page

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        header_label = QLabel("Dashboard - Plan Saved Task")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        content_layout = QHBoxLayout()

        self.dashboard_calendar = QCalendarWidget()
        self.dashboard_calendar.setFixedWidth(int(self.width() * 0.3))
        self.dashboard_calendar.setSelectedDate(QDate.currentDate())
        self.dashboard_calendar.selectionChanged.connect(self.update_dashboard)
        content_layout.addWidget(self.dashboard_calendar)

        task_widget = QWidget()
        task_layout = QVBoxLayout(task_widget)
        
        self.task_date_label = QLabel(f"Tasks for {QDate.currentDate().toString('MMMM d, yyyy')}")
        self.task_date_label.setFont(QFont("Arial", 12))
        task_layout.addWidget(self.task_date_label)
        
        self.dashboard_list = QListWidget()
        self.dashboard_list.setSpacing(5)
        task_layout.addWidget(self.dashboard_list, 1)
        
        content_layout.addWidget(task_widget, 2)
        layout.addLayout(content_layout)

        self.update_dashboard()
        
        return page

    def add_task(self):
        task = self.task_input.text().strip()
        if task:
            InsertRow("Tasks", {"Name": task})
            self.task_input.clear()
            self.load_tasks()
            self.load_existing_tasks()

    def edit_task(self, task_id):
        tasks = GetAllRows("Tasks")
        current_task = next((task for task in tasks if task["TaskId"] == task_id), None)
        if current_task:
            new_task, ok = QInputDialog.getText(self, "Edit Task", "Enter new task name:", QLineEdit.Normal, current_task["Name"])
            if ok and new_task.strip():
                UpdateRow("Tasks", {"Name": new_task.strip(), "TaskId": task_id}, "TaskId")
                schedules = GetAllRows("TaskSchedules")
                for schedule in schedules:
                    if schedule["TaskId"] == task_id:
                        schedule["Name"] = new_task.strip()
                        UpdateRow("TaskSchedules", schedule, "ScheduleId")
                self.load_tasks()
                self.load_existing_tasks()
                self.update_date_task_order_list()
                self.update_dashboard()

    def delete_task(self, date, task_id_or_schedule_id):
        if date is None:
            RemoveRow("Tasks", "TaskId", task_id_or_schedule_id)
            schedules = GetAllRows("TaskSchedules")
            for schedule in schedules:
                if schedule["TaskId"] == task_id_or_schedule_id:
                    RemoveRow("TaskSchedules", "ScheduleId", schedule["ScheduleId"])
        else:
            RemoveRow("TaskSchedules", "ScheduleId", task_id_or_schedule_id)
        self.load_tasks()
        self.load_existing_tasks()
        self.update_date_task_order_list()
        dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
        if date is None or date == dashboard_date:
            self.update_dashboard()

    def add_existing_tasks(self):
        date = self.date_picker.selectedDate().toString("yyyy-MM-dd")
        for item in self.existing_task_list.selectedItems():
            task_id = int(item.data(Qt.UserRole))
            task_name = item.text()
            schedules = GetAllRows("TaskSchedules")
            if not any(s for s in schedules if s["TaskId"] == task_id and s["Date"] == date):
                next_order = max([s["OrderIndex"] for s in schedules if s["Date"] == date], default=-1) + 1
                InsertRow("TaskSchedules", {
                    "TaskId": task_id,
                    "Name": task_name,
                    "Date": date,
                    "OrderIndex": next_order,
                    "Completed": 0
                })
        self.update_date_task_order_list()
        dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
        if date == dashboard_date:
            self.update_dashboard()

    def add_new_task(self):
        date = self.date_picker.selectedDate().toString("yyyy-MM-dd")
        task = self.date_task_input.text().strip()
        if task:
            schedules = GetAllRows("TaskSchedules")
            next_order = max([s["OrderIndex"] for s in schedules if s["Date"] == date], default=-1) + 1
            InsertRow("TaskSchedules", {
                "TaskId": 0,
                "Name": task,
                "Date": date,
                "OrderIndex": next_order,
                "Completed": 0
            })
            self.date_task_input.clear()
        self.update_date_task_order_list()
        dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
        if date == dashboard_date:
            self.update_dashboard()

    def load_tasks(self):
        self.task_list.clear()
        tasks = GetAllRows("Tasks")
        for task in tasks:
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            label = QLabel(task["Name"])
            layout.addWidget(label, 1)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedWidth(50)
            edit_btn.clicked.connect(lambda _, tid=task["TaskId"]: self.edit_task(tid))
            layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedWidth(30)
            delete_btn.clicked.connect(lambda _, tid=task["TaskId"]: self.delete_task(None, tid))
            layout.addWidget(delete_btn)
            
            layout.setContentsMargins(10, 5, 10, 5)
            widget.setLayout(layout)
            
            size = widget.sizeHint()
            new_size = QSize(size.width(), size.height() + 20)
            item.setSizeHint(new_size)
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)

    def load_existing_tasks(self):
        self.existing_task_list.clear()
        tasks = GetAllRows("Tasks")
        for task in tasks:
            item = QListWidgetItem(task["Name"])
            item.setData(Qt.UserRole, task["TaskId"])
            size = QSize(0, 40)
            item.setSizeHint(size)
            self.existing_task_list.addItem(item)

    def update_date_task_order_list(self):
        self.date_task_order_list.clear()
        date = self.date_picker.selectedDate().toString("yyyy-MM-dd")
        schedules = GetAllRows("TaskSchedules")
        date_schedules = [s for s in schedules if s["Date"] == date]
        date_schedules.sort(key=lambda x: x["OrderIndex"])
        
        for i, schedule in enumerate(date_schedules):
            item = QListWidgetItem()
            item.setData(Qt.UserRole, schedule["ScheduleId"])
            item.setData(Qt.UserRole + 1, schedule["Name"])
            
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            label = QLabel(schedule["Name"])
            layout.addWidget(label, 1)
            
            up_btn = QPushButton("↑")
            up_btn.setFixedWidth(30)
            up_btn.clicked.connect(lambda _, idx=i: self.move_task_up(date, idx))
            layout.addWidget(up_btn)
            
            down_btn = QPushButton("↓")
            down_btn.setFixedWidth(30)
            down_btn.clicked.connect(lambda _, idx=i: self.move_task_down(date, idx))
            layout.addWidget(down_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedWidth(30)
            delete_btn.clicked.connect(lambda _, sid=schedule["ScheduleId"]: self.delete_task(date, sid))
            layout.addWidget(delete_btn)
            
            layout.setContentsMargins(10, 5, 10, 5)
            widget.setLayout(layout)
            
            size = widget.sizeHint()
            new_size = QSize(size.width(), size.height() + 20)
            item.setSizeHint(new_size)
            self.date_task_order_list.addItem(item)
            self.date_task_order_list.setItemWidget(item, widget)
        
        self.date_task_order_list.model().rowsMoved.connect(self.save_task_order)

    def move_task_up(self, date, index):
        schedules = GetAllRows("TaskSchedules")
        date_schedules = [s for s in schedules if s["Date"] == date]
        date_schedules.sort(key=lambda x: x["OrderIndex"])
        if index > 0:
            date_schedules[index]["OrderIndex"], date_schedules[index-1]["OrderIndex"] = \
                date_schedules[index-1]["OrderIndex"], date_schedules[index]["OrderIndex"]
            UpdateRow("TaskSchedules", date_schedules[index], "ScheduleId")
            UpdateRow("TaskSchedules", date_schedules[index-1], "ScheduleId")
            self.update_date_task_order_list()
            dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
            if date == dashboard_date:
                self.update_dashboard()

    def move_task_down(self, date, index):
        schedules = GetAllRows("TaskSchedules")
        date_schedules = [s for s in schedules if s["Date"] == date]
        date_schedules.sort(key=lambda x: x["OrderIndex"])
        if index < len(date_schedules) - 1:
            date_schedules[index]["OrderIndex"], date_schedules[index+1]["OrderIndex"] = \
                date_schedules[index+1]["OrderIndex"], date_schedules[index]["OrderIndex"]
            UpdateRow("TaskSchedules", date_schedules[index], "ScheduleId")
            UpdateRow("TaskSchedules", date_schedules[index+1], "ScheduleId")
            self.update_date_task_order_list()
            dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
            if date == dashboard_date:
                self.update_dashboard()

    def save_task_order(self):
        date = self.date_picker.selectedDate().toString("yyyy-MM-dd")
        schedules = GetAllRows("TaskSchedules")
        date_schedules = [s for s in schedules if s["Date"] == date]
        for i in range(self.date_task_order_list.count()):
            item = self.date_task_order_list.item(i)
            schedule_id = item.data(Qt.UserRole)
            schedule = next(s for s in date_schedules if s["ScheduleId"] == schedule_id)
            schedule["OrderIndex"] = i
            UpdateRow("TaskSchedules", schedule, "ScheduleId")
        self.update_date_task_order_list()
        dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
        if date == dashboard_date:
            self.update_dashboard()

    def update_dashboard(self):
        self.dashboard_list.clear()
        date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
        self.task_date_label.setText(f"Tasks for {self.dashboard_calendar.selectedDate().toString('MMMM d, yyyy')}")
        schedules = GetAllRows("TaskSchedules")
        date_schedules = [s for s in schedules if s["Date"] == date]
        date_schedules.sort(key=lambda x: x["OrderIndex"])
        
        for i, schedule in enumerate(date_schedules):
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            label = QLabel(schedule["Name"])
            layout.addWidget(label, 1)
            
            checkbox = QCheckBox()
            checkbox.setChecked(bool(schedule["Completed"]))
            checkbox.stateChanged.connect(lambda state, sid=schedule["ScheduleId"]: self.toggle_task_completion(sid, state))
            layout.addWidget(checkbox)
            
            layout.setContentsMargins(10, 5, 10, 5)
            widget.setLayout(layout)
            
            size = widget.sizeHint()
            new_size = QSize(size.width(), size.height() + 20)
            item.setSizeHint(new_size)
            self.dashboard_list.addItem(item)
            self.dashboard_list.setItemWidget(item, widget)

    def toggle_task_completion(self, schedule_id, state):
        schedule = next(s for s in GetAllRows("TaskSchedules") if s["ScheduleId"] == schedule_id)
        schedule["Completed"] = 1 if state else 0
        UpdateRow("TaskSchedules", schedule, "ScheduleId")
        self.update_dashboard()

if __name__ == '__main__':
    CreateDatabase(PersonalAssistantTom)
    Hw_Db_TableInitialization()
    app = QApplication(sys.argv)
    window = TaskPlanner()
    window.show()
    sys.exit(app.exec_())