import enum


class UserRole(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    RECEPTIONIST = "RECEPTIONIST"
    ADMIN = "ADMIN"


class BedStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    CLEANING = "CLEANING"
    MAINTENANCE = "MAINTENANCE"
    RESERVED = "RESERVED"


class PriorityLevel(str, enum.Enum):
    NORMAL = "NORMAL"
    URGENT = "URGENT"
    EMERGENCY = "EMERGENCY"


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CHECKED_IN = "CHECKED_IN"
    IN_QUEUE = "IN_QUEUE"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class QueueStatus(str, enum.Enum):
    WAITING = "WAITING"
    CALLED = "CALLED"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
