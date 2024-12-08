from PyQt5.QtCore import QTimer

class Controller:
    def __init__(self, view):
        self.view = view
        self.depth = 0
        self.velocity = 10
        self.acceleration = 5

        # Update the status label with initial values
        self.update_status_view()

        # Timer for periodic updates (as an example)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_values)
        self.timer.start(1000)  # Update every second

    def update_values(self):
        # Sample logic for changing values
        self.depth += 1
        self.velocity += 1
        self.acceleration += 1
        
        # Update the view with new values
        self.update_status_view()

    def update_status_view(self):
        # Update the status label in the view
        self.view.status_view.setText(f"Depth: {self.depth}\nVelocity: {self.velocity}\nAcceleration: {self.acceleration}")