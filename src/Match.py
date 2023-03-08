
from dataclasses import dataclass
import string

@dataclass
class Match:
    tournamentId: string
    league: string
    streamChannel: string
    streamSource: string
