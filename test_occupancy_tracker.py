
from occupancy_tracker import OccupancyTracker
from classrooms import classrooms


tracker = OccupancyTracker()

tracker.update("VED226", 25)
tracker.update("VED329", 40)

print("VED226 count:", tracker.get_count("VED226"))
print("VED329 count:", tracker.get_count("VED329"))
print("Available rooms:", tracker.get_available_rooms(classrooms))
