import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QListWidget, QLineEdit, QCalendarWidget, 
                            QLabel, QListWidgetItem, QCheckBox, QInputDialog)
from PyQt5.QtCore import QDate, Qt, QSize
from PyQt5.QtGui import QFont

# Import all database functions from Sql.py
from Sql import *

class TaskPlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Task Planner")

        # Get screen size and set window to 80% of screen dimensions, but start maximized
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
        self.showMaximized()  # Start in maximized mode

        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Sidebar (App Drawer) on the left
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(150)  # Increased width to accommodate button text
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)

        # Add navigation buttons to the sidebar in the specified order with renamed labels
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

        # Stacked widget for pages on the right
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget, 1)  # Stretch to fill remaining space

        # Create pages
        self.task_list_page = self.create_task_list_page()
        self.date_task_page = self.create_date_task_page()
        self.dashboard_page = self.create_dashboard_page()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.task_list_page)  # Index 0
        self.stacked_widget.addWidget(self.date_task_page)  # Index 1
        self.stacked_widget.addWidget(self.dashboard_page)  # Index 2

        # Set default page to Dashboard (index 2)
        self.stacked_widget.setCurrentIndex(2)

    def create_task_list_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        # Header: "Pre Saved Task - General Tasks"
        header_label = QLabel("Pre Saved Task - General Tasks")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Task input
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task")
        layout.addWidget(self.task_input)
        
        # Add task button
        add_btn = QPushButton("Add Task")
        add_btn.clicked.connect(self.add_task)
        layout.addWidget(add_btn)
        
        # Task list
        self.task_list = QListWidget()
        self.task_list.setSpacing(5)  # Add spacing between items
        layout.addWidget(self.task_list, 1)  # Stretch to fill space
        
        # Load existing tasks
        self.load_tasks()
        
        return page

    def create_date_task_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        # Header: "Plan Task - Add Date-wise Task"
        header_label = QLabel("Plan Task - Add Date-wise Task")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Main content: Split into left (calendar + existing tasks), middle (arrow button), and right (new task + reorder)
        content_layout = QHBoxLayout()

        # Left: Calendar and existing tasks (30% width)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Calendar widget for date selection
        self.date_picker = QCalendarWidget()
        self.date_picker.setFixedWidth(int(self.width() * 0.3))
        self.date_picker.setSelectedDate(QDate.currentDate())
        self.date_picker.selectionChanged.connect(self.update_date_task_order_list)
        left_layout.addWidget(self.date_picker)

        # Existing tasks selection
        left_layout.addWidget(QLabel("Select Existing Tasks:"))
        self.existing_task_list = QListWidget()
        self.existing_task_list.setSelectionMode(QListWidget.MultiSelection)
        self.existing_task_list.setSpacing(5)  # Add spacing between items
        self.load_existing_tasks()
        left_layout.addWidget(self.existing_task_list, 1)  # Stretch to fill space

        content_layout.addWidget(left_widget)

        # Middle: Right arrow button to add selected existing tasks
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setAlignment(Qt.AlignCenter)
        add_existing_btn = QPushButton("→")
        add_existing_btn.setFixedSize(40, 40)
        add_existing_btn.clicked.connect(self.add_existing_tasks)
        middle_layout.addWidget(add_existing_btn)
        content_layout.addWidget(middle_widget)

        # Right: New task input and task reordering (70% width)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # New task input
        self.date_task_input = QLineEdit()
        self.date_task_input.setPlaceholderText("Enter new task for selected date")
        right_layout.addWidget(self.date_task_input)

        # Add task button (for new task only)
        add_new_task_btn = QPushButton("Add New Task")
        add_new_task_btn.clicked.connect(self.add_new_task)
        right_layout.addWidget(add_new_task_btn)

        # Task order list for the selected date
        right_layout.addWidget(QLabel("Tasks for Selected Date (Drag to Reorder or Use Buttons):"))
        self.date_task_order_list = QListWidget()
        self.date_task_order_list.setDragDropMode(QListWidget.InternalMove)
        self.date_task_order_list.setSpacing(5)  # Add spacing between items
        right_layout.addWidget(self.date_task_order_list, 1)  # Stretch to fill space

        content_layout.addWidget(right_widget, 2)  # 2:1 ratio for right vs left
        layout.addLayout(content_layout)

        # Initial update of task order list
        self.update_date_task_order_list()

        return page

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        # Header: "Dashboard - Plan Saved Task"
        header_label = QLabel("Dashboard - Plan Saved Task")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Main content: Split into calendar and task list
        content_layout = QHBoxLayout()

        # Left: Calendar widget (30% width)
        self.dashboard_calendar = QCalendarWidget()
        self.dashboard_calendar.setFixedWidth(int(self.width() * 0.3))
        self.dashboard_calendar.setSelectedDate(QDate.currentDate())
        self.dashboard_calendar.selectionChanged.connect(self.update_dashboard)
        content_layout.addWidget(self.dashboard_calendar)

        # Right: Task list with checkboxes (70% width)
        task_widget = QWidget()
        task_layout = QVBoxLayout(task_widget)
        
        # Label for tasks
        self.task_date_label = QLabel(f"Tasks for {QDate.currentDate().toString('MMMM d, yyyy')}")
        self.task_date_label.setFont(QFont("Arial", 12))
        task_layout.addWidget(self.task_date_label)
        
        # Task list
        self.dashboard_list = QListWidget()
        self.dashboard_list.setSpacing(5)  # Add spacing between items
        task_layout.addWidget(self.dashboard_list, 1)  # Stretch to fill space
        
        content_layout.addWidget(task_widget, 2)  # 2:1 ratio for task list vs calendar
        layout.addLayout(content_layout)

        # Initial update of tasks
        self.update_dashboard()
        
        return page

    def add_task(self):
        task = self.task_input.text().strip()
        if task:
            # Insert the task into the Tasks table
            task_id = InsertRow("Tasks", {"Name": task})
            self.task_input.clear()
            self.load_tasks()  # Refresh the task list
            self.load_existing_tasks()  # Update existing tasks in date-wise page

    def edit_task(self, task_id):
        # Fetch the current task name
        tasks = GetAllRows("Tasks")
        current_task = next((task for task in tasks if task["TaskId"] == task_id), None)
        if current_task:
            new_task, ok = QInputDialog.getText(self, "Edit Task", "Enter new task name:", QLineEdit.Normal, current_task["Name"])
            if ok and new_task.strip():
                # Update the task in the Tasks table
                UpdateRow("Tasks", {"Name": new_task.strip(), "TaskId": task_id}, "TaskId")
                # Refresh the lists
                self.load_tasks()
                self.load_existing_tasks()
                self.update_date_task_order_list()
                self.update_dashboard()

    def delete_task(self, date, task_id_or_schedule_id):
        if date is None:
            # Delete from general tasks (Tasks table)
            RemoveRow("Tasks", "TaskId", task_id_or_schedule_id)
            # Also delete associated schedules
            RemoveRow("TaskSchedules", "TaskId", task_id_or_schedule_id)
        else:
            # Delete from TaskSchedules for a specific date
            RemoveRow("TaskSchedules", "ScheduleId", task_id_or_schedule_id)
        # Refresh the lists
        self.load_tasks()
        self.load_existing_tasks()
        self.update_date_task_order_list()
        # Update dashboard if the deleted task's date matches the dashboard's current date
        dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
        if date is None or date == dashboard_date:
            self.update_dashboard()

    def add_existing_tasks(self):
        date = self.date_picker.selectedDate().toString("yyyy-MM-dd")
        # Add selected existing tasks
        for item in self.existing_task_list.selectedItems():
            task_id = int(item.data(Qt.UserRole))
            # Check if the task already exists for this date
            schedules = GetAllRows("TaskSchedules")
            if not any(s for s in schedules if s["TaskId"] == task_id and s["Date"] == date):
                # Add to TaskSchedules with the next OrderIndex
                existing_schedules = [s for s in schedules if s["Date"] == date]
                next_order = max([s["OrderIndex"] for s in existing_schedules], default=-1) + 1
                InsertRow("TaskSchedules", {
                    "TaskId": task_id,
                    "Date": date,
                    "OrderIndex": next_order,
                    "Completed": 0
                })
        # Update task order list
        self.update_date_task_order_list()
        # Update dashboard if the added task's date matches the dashboard's current date
        dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
        if date == dashboard_date:
            self.update_dashboard()

    def add_new_task(self):
        date = self.date_picker.selectedDate().toString("yyyy-MM-dd")
        task = self.date_task_input.text().strip()
        if task:
            # First, add to Tasks table
            task_id = InsertRow("Tasks", {"Name": task})
            # Then, add to TaskSchedules with the next OrderIndex
            schedules = GetAllRows("TaskSchedules")
            existing_schedules = [s for s in schedules if s["Date"] == date]
            next_order = max([s["OrderIndex"] for s in existing_schedules], default=-1) + 1
            InsertRow("TaskSchedules", {
                "TaskId": task_id,
                "Date": date,
                "OrderIndex": next_order,
                "Completed": 0
            })
            self.date_task_input.clear()
        # Update task order list
        self.update_date_task_order_list()
        # Update dashboard if the added task's date matches the dashboard's current date
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
            
            # Task label
            label = QLabel(task["Name"])
            layout.addWidget(label, 1)  # Stretch to take more space
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedWidth(50)
            edit_btn.clicked.connect(lambda _, tid=task["TaskId"]: self.edit_task(tid))
            layout.addWidget(edit_btn)
            
            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedWidth(30)
            delete_btn.clicked.connect(lambda _, tid=task["TaskId"]: self.delete_task(None, tid))
            layout.addWidget(delete_btn)
            
            layout.setContentsMargins(10, 5, 10, 5)  # Add padding for better spacing
            widget.setLayout(layout)
            
            # Increase row height
            size = widget.sizeHint()
            new_size = QSize(size.width(), size.height() + 20)  # Increase height by 20 pixels
            item.setSizeHint(new_size)
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)

    def load_existing_tasks(self):
        self.existing_task_list.clear()
        tasks = GetAllRows("Tasks")
        for task in tasks:
            item = QListWidgetItem(task["Name"])
            # Store TaskId in the item's data
            item.setData(Qt.UserRole, task["TaskId"])
            # Increase row height for existing tasks
            size = QSize(0, 40)  # Fixed height for consistency
            item.setSizeHint(size)
            self.existing_task_list.addItem(item)

    def update_date_task_order_list(self):
        self.date_task_order_list.clear()
        date = self.date_picker.selectedDate().toString("yyyy-MM-dd")
        # Fetch schedules for this date, joined with task names
        schedules = GetAllRows("TaskSchedules")
        tasks = GetAllRows("Tasks")
        date_schedules = [s for s in schedules if s["Date"] == date]
        date_schedules.sort(key=lambda x: x["OrderIndex"])
        
        for i, schedule in enumerate(date_schedules):
            task = next(t for t in tasks if t["TaskId"] == schedule["TaskId"])
            item = QListWidgetItem()
            # Store the schedule ID and task name in the item's data
            item.setData(Qt.UserRole, schedule["ScheduleId"])
            item.setData(Qt.UserRole + 1, task["Name"])
            
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            # Task label
            label = QLabel(task["Name"])
            layout.addWidget(label, 1)  # Stretch to take more space
            
            # Up button
            up_btn = QPushButton("↑")
            up_btn.setFixedWidth(30)
            up_btn.clicked.connect(lambda _, idx=i: self.move_task_up(date, idx))
            layout.addWidget(up_btn)
            
            # Down button
            down_btn = QPushButton("↓")
            down_btn.setFixedWidth(30)
            down_btn.clicked.connect(lambda _, idx=i: self.move_task_down(date, idx))
            layout.addWidget(down_btn)
            
            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedWidth(30)
            delete_btn.clicked.connect(lambda _, sid=schedule["ScheduleId"]: self.delete_task(date, sid))
            layout.addWidget(delete_btn)
            
            layout.setContentsMargins(10, 5, 10, 5)  # Add padding for better spacing
            widget.setLayout(layout)
            
            # Increase row height
            size = widget.sizeHint()
            new_size = QSize(size.width(), size.height() + 20)  # Increase height by 20 pixels
            item.setSizeHint(new_size)
            self.date_task_order_list.addItem(item)
            self.date_task_order_list.setItemWidget(item, widget)
        
        # Update tasks order when items are reordered in drag-and-drop
        self.date_task_order_list.model().rowsMoved.connect(self.save_task_order)

    def move_task_up(self, date, index):
        schedules = GetAllRows("TaskSchedules")
        date_schedules = [s for s in schedules if s["Date"] == date]
        date_schedules.sort(key=lambda x: x["OrderIndex"])
        if index > 0:
            # Swap OrderIndex with the previous task
            date_schedules[index]["OrderIndex"], date_schedules[index-1]["OrderIndex"] = \
                date_schedules[index-1]["OrderIndex"], date_schedules[index]["OrderIndex"]
            UpdateRow("TaskSchedules", date_schedules[index], "ScheduleId")
            UpdateRow("TaskSchedules", date_schedules[index-1], "ScheduleId")
            self.update_date_task_order_list()
            # Update dashboard if the modified date matches the dashboard's current date
            dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
            if date == dashboard_date:
                self.update_dashboard()

    def move_task_down(self, date, index):
        schedules = GetAllRows("TaskSchedules")
        date_schedules = [s for s in schedules if s["Date"] == date]
        date_schedules.sort(key=lambda x: x["OrderIndex"])
        if index < len(date_schedules) - 1:
            # Swap OrderIndex with the next task
            date_schedules[index]["OrderIndex"], date_schedules[index+1]["OrderIndex"] = \
                date_schedules[index+1]["OrderIndex"], date_schedules[index]["OrderIndex"]
            UpdateRow("TaskSchedules", date_schedules[index], "ScheduleId")
            UpdateRow("TaskSchedules", date_schedules[index+1], "ScheduleId")
            self.update_date_task_order_list()
            # Update dashboard if the modified date matches the dashboard's current date
            dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
            if date == dashboard_date:
                self.update_dashboard()

    def save_task_order(self):
        date = self.date_picker.selectedDate().toString("yyyy-MM-dd")
        schedules = GetAllRows("TaskSchedules")
        date_schedules = [s for s in schedules if s["Date"] == date]
        # Update OrderIndex based on new order
        for i in range(self.date_task_order_list.count()):
            item = self.date_task_order_list.item(i)
            schedule_id = item.data(Qt.UserRole)
            schedule = next(s for s in date_schedules if s["ScheduleId"] == schedule_id)
            schedule["OrderIndex"] = i
            UpdateRow("TaskSchedules", schedule, "ScheduleId")
        self.update_date_task_order_list()
        # Update dashboard if the modified date matches the dashboard's current date
        dashboard_date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
        if date == dashboard_date:
            self.update_dashboard()

    def update_dashboard(self):
        self.dashboard_list.clear()
        date = self.dashboard_calendar.selectedDate().toString("yyyy-MM-dd")
        self.task_date_label.setText(f"Tasks for {self.dashboard_calendar.selectedDate().toString('MMMM d, yyyy')}")
        schedules = GetAllRows("TaskSchedules")
        tasks = GetAllRows("Tasks")
        date_schedules = [s for s in schedules if s["Date"] == date]
        date_schedules.sort(key=lambda x: x["OrderIndex"])
        
        for i, schedule in enumerate(date_schedules):
            task = next(t for t in tasks if t["TaskId"] == schedule["TaskId"])
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            # Task label on the left
            label = QLabel(task["Name"])
            layout.addWidget(label, 1)  # Stretch to take more space
            
            # Checkbox on the right
            checkbox = QCheckBox()
            checkbox.setChecked(bool(schedule["Completed"]))
            checkbox.stateChanged.connect(lambda state, sid=schedule["ScheduleId"]: self.toggle_task_completion(sid, state))
            layout.addWidget(checkbox)
            
            layout.setContentsMargins(10, 5, 10, 5)  # Add padding for better spacing
            widget.setLayout(layout)
            
            # Increase row height
            size = widget.sizeHint()
            new_size = QSize(size.width(), size.height() + 20)  # Increase height by 20 pixels
            item.setSizeHint(new_size)
            self.dashboard_list.addItem(item)
            self.dashboard_list.setItemWidget(item, widget)

    def toggle_task_completion(self, schedule_id, state):
        schedule = next(s for s in GetAllRows("TaskSchedules") if s["ScheduleId"] == schedule_id)
        schedule["Completed"] = 1 if state else 0
        UpdateRow("TaskSchedules", schedule, "ScheduleId")
        self.update_dashboard()

if __name__ == '__main__':
    # Initialize Database
    CreateDatabase(PersonalAssistantTom)
    Hw_Db_TableInitialization()
    app = QApplication(sys.argv)
    window = TaskPlanner()
    window.show()
    sys.exit(app.exec_())