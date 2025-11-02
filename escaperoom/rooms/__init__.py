<<<<<<< HEAD
# just export rooms so i can import them easily
=======
"""Makes all room classes easy to import.
This lets the game engine load each room directly from escaperoom.rooms."""

>>>>>>> kim
from .intro import IntroRoom
from .soc import SocRoom
from .dns import DnsRoom
from .vault import VaultRoom
from .malware import MalwareRoom
from .final import FinalGateRoom

__all__ = [
    "IntroRoom",
    "SocRoom",
    "DnsRoom",
    "VaultRoom",
    "MalwareRoom",
    "FinalGateRoom",
<<<<<<< HEAD
]

=======
]
>>>>>>> kim
