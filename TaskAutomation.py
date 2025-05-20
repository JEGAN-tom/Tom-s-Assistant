import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QListWidget, QLineEdit, QDateEdit, 
                            QLabel, QListWidgetItem, QCheckBox)
from PyQt5.QtCore import QDate, Qt

class TaskPlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Task Planner")

        # Get screen size and set window to 80% of screen dimensions
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

        # Initialize task storage (dictionary: date -> list of {"text": task, "completed": bool}, None for general tasks)
        self.tasks = {None: []}

        # Central widget and stacked widget for pages
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget, 1)  # Stretch factor to make it responsive

        # Create pages
        self.task_list_page = self.create_task_list_page()
        self.date_task_page = self.create_date_task_page()
        self.dashboard_page = self.create_dashboard_page()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.task_list_page)
        self.stacked_widget.addWidget(self.date_task_page)
        self.stacked_widget.addWidget(self.dashboard_page)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.btn_task_list = QPushButton("Task List")
        self.btn_date_task = QPushButton("Add Date-wise Task")
        self.btn_dashboard = QPushButton("Dashboard")
        
        self.btn_task_list.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.btn_date_task.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_dashboard.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        
        nav_layout.addWidget(self.btn_task_list)
        nav_layout.addWidget(self.btn_date_task)
        nav_layout.addWidget(self.btn_dashboard)
        self.layout.addLayout(nav_layout)

    def create_task_list_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
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
        layout.addWidget(self.task_list, 1)  # Stretch to fill space
        
        # Load existing tasks
        self.load_tasks()
        
        return page

    def create_date_task_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Date picker
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Select Date:"))
        layout.addWidget(self.date_picker)
        
        # Existing tasks selection
        layout.addWidget(QLabel("Select Existing Tasks:"))
        self.existing_task_list = QListWidget()
        self.existing_task_list.setSelectionMode(QListWidget.MultiSelection)
        self.load_existing_tasks()
        layout.addWidget(self.existing_task_list, 1)  # Stretch to fill space
        
        # New task input
        self.date_task_input = QLineEdit()
        self.date_task_input.setPlaceholderText("Enter new task for selected date")
        layout.addWidget(self.date_task_input)
        
        # Add task button
        add_date_task_btn = QPushButton("Add Selected and New Tasks")
        add_date_task_btn.clicked.connect(self.add_date_task)
        layout.addWidget(add_date_task_btn)
        
        # Task order list for the selected date
        layout.addWidget(QLabel("Tasks for Selected Date (Drag to Reorder or Use Buttons):"))
        self.date_task_order_list = QListWidget()
        self.date_task_order_list.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(self.date_task_order_list, 1)  # Stretch to fill space
        
        # Update task order list when date changes
        self.date_picker.dateChanged.connect(self.update_date_task_order_list)
        self.update_date_task_order_list()
        
        return page

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Date selector
        self.dashboard_date = QDateEdit()
        self.dashboard_date.setCalendarPopup(True)
        self.dashboard_date.setDate(QDate.currentDate())
        self.dashboard_date.dateChanged.connect(self.update_dashboard)
        layout.addWidget(QLabel("Select Date to View Tasks:"))
        layout.addWidget(self.dashboard_date)
        
        # Task display
        self.dashboard_list = QListWidget()
        layout.addWidget(self.dashboard_list, 1)  # Stretch to fill space
        
        # Initial update
        self.update_dashboard()
        
        return page

    def add_task(self):
        task = self.task_input.text().strip()
        if task:
            self.tasks[None].append({"text": task, "completed": False})
            self.task_list.addItem(task)
            self.task_input.clear()
            self.load_existing_tasks()  # Update existing tasks in date-wise page

    def add_date_task(self):
        date = self.date_picker.date().toString("yyyy-MM-dd")
        if date not in self.tasks:
            self.tasks[date] = []
            
        # Add selected existing tasks
        for item in self.existing_task_list.selectedItems():
            task = item.text()
            if not any(t["text"] == task for t in self.tasks[date]):
                self.tasks[date].append({"text": task, "completed": False})
        
        # Add new task
        task = self.date_task_input.text().strip()
        if task:
            self.tasks[date].append({"text": task, "completed": False})
            self.date_task_input.clear()
        
        # Update task order list
        self.update_date_task_order_list()

    def load_tasks(self):
        self.task_list.clear()
        for task in self.tasks.get(None, []):
            self.task_list.addItem(task["text"])

    def load_existing_tasks(self):
        self.existing_task_list.clear()
        for task in self.tasks.get(None, []):
            self.existing_task_list.addItem(task["text"])

    def update_date_task_order_list(self):
        self.date_task_order_list.clear()
        date = self.date_picker.date().toString("yyyy-MM-dd")
        tasks = self.tasks.get(date, [])
        
        for i, task in enumerate(tasks):
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            # Task label
            label = QLabel(task["text"])
            layout.addWidget(label)
            
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
            
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.date_task_order_list.addItem(item)
            self.date_task_order_list.setItemWidget(item, widget)
        
        # Update tasks order when items are reordered in drag-and-drop
        self.date_task_order_list.model().rowsMoved.connect(self.save_task_order)

    def move_task_up(self, date, index):
        if index > 0:
            self.tasks[date][index], self.tasks[date][index-1] = self.tasks[date][index-1], self.tasks[date][index]
            self.update_date_task_order_list()

    def move_task_down(self, date, index):
        if index < len(self.tasks[date]) - 1:
            self.tasks[date][index], self.tasks[date][index+1] = self.tasks[date][index+1], self.tasks[date][index]
            self.update_date_task_order_list()

    def save_task_order(self):
        date = self.date_picker.date().toString("yyyy-MM-dd")
        new_order = []
        for i in range(self.date_task_order_list.count()):
            widget = self.date_task_order_list.itemWidget(self.date_task_order_list.item(i))
            label = widget.findChild(QLabel).text()
            new_order.append(label)
        # Rebuild tasks list maintaining completion status
        old_tasks = {t["text"]: t["completed"] for t in self.tasks[date]}
        self.tasks[date] = [{"text": text, "completed": old_tasks.get(text, False)} for text in new_order]

    def update_dashboard(self):
        self.dashboard_list.clear()
        date = self.dashboard_date.date().toString("yyyy-MM-dd")
        for i, task in enumerate(self.tasks.get(date, [])):
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout(widget)
            checkbox = QCheckBox()
            checkbox.setChecked(task["completed"])
            checkbox.stateChanged.connect(lambda state, idx=i: self.toggle_task_completion(date, idx, state))
            label = QLabel(task["text"])
            layout.addWidget(checkbox)
            layout.addWidget(label)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.dashboard_list.addItem(item)
            self.dashboard_list.setItemWidget(item, widget)

    def toggle_task_completion(self, date, index, state):
        self.tasks[date][index]["completed"] = bool(state)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskPlanner()
    window.show()
    sys.exit(app.exec_())