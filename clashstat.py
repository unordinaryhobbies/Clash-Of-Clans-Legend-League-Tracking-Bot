import coc  #type: ignore
import nest_asyncio  #type: ignore
import asyncio
from typing import List, Dict, Optional, Union, Any


class PlayerStats():
    def __init__(self, ID: str, Password: str, filename: str) -> None:
        nest_asyncio.apply()
        self.__ID: str = ID
        self.__PW: str = Password
        self.PlayersTag: List[str] = []
        self.PrevPlayersFullInfo: Dict[str, Dict[str, Union[str, int]]] = {}
        self.client = coc.login(self.__ID, self.__PW)
        self.tags_collection_filename: str = filename

    def __del__(self) -> None:
        try:
            self.client.close()
            print("Client Closed")
        except Exception:
            print("Client close failed")

    async def GetUserTrophies(self) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        User Data in self.PlayersTag
        Get user's trophies from the coc.client api
        
        return list of dict[playertag, dict[player name, tag, trophies]]
        why?: to find playertag within O(1)
        """
        tasks = list(
            map(
                lambda player: asyncio.create_task(
                    self.client.get_player(player)), self.PlayersTag))

        PlayersInfo = await asyncio.gather(*tasks)

        return dict(map(lambda player: \
            (player.tag, {'name': player.name, 'tag': player.tag, 'trophies': player.trophies})\
                ,PlayersInfo))

    def GetPlayerList(self) -> None:
        """
        Get target player tag from the given filename and store it in self.PlayersTag
        """
        with open(self.tags_collection_filename, 'r') as f:
            while True:
                tag = f.readline()
                if tag == '':
                    break
                tag = tag.replace('\n', '')
                self.PlayersTag.append(tag)

    def ComparePlayerData(self, NewPlayersInfo: Dict[str, Dict[str, Union[str, int]]])\
         -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Compare trophies of NewPlayersInfo with self.PrevPlayersFullInfo
        if some of them are different, return the players in dict{playertag, playerinfo} format
        that have different trophy value 
        """

        def IsItSameTrophies(profile_1: Optional[Dict[str, Union[str, int]]],\
             profile_2: Optional[Dict[str, Union[str, int]]]) -> bool:

            if isinstance(profile_1, type(None)) and isinstance(
                    profile_2, type(None)):
                return False
            return profile_1.get('trophies') == profile_2.get(
                'trophies')  #type: ignore

        #If nothing is in the prev player info list
        #return every player info
        if len(self.PrevPlayersFullInfo.keys()) == 0:
            return NewPlayersInfo

        UpdateRequiredInfo: Dict[str, Dict[str, Union[str, int]]] = {}
        for tag in self.PlayersTag:
            if not IsItSameTrophies(NewPlayersInfo.get(tag),
                                    self.PrevPlayersFullInfo.get(tag)):
                UpdateRequiredInfo[tag] = NewPlayersInfo[tag]

        return UpdateRequiredInfo

    def FindTrophyDifferenceAndUpdate(
        self, NewPlayersInfo: Dict[str, Dict[str, Union[str, int]]]
    ) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Get the difference in trophy and return the information
        """
        if len(self.PrevPlayersFullInfo.keys()) == 0:
            return {}

        FindTrophyDifference = lambda CurrInfo, PastInfo: CurrInfo.get(
            'trophies') - PastInfo.get('trophies')

        TrophyDifferenceCollection = {}
        for tag in NewPlayersInfo.keys():
            TrophyDifference = FindTrophyDifference(
                NewPlayersInfo[tag], self.PrevPlayersFullInfo[tag])
            TrophyDifferenceCollection[tag] = \
                {'trophies': TrophyDifference, 'name': NewPlayersInfo[tag].get('name'), 'tag': tag}

            self.PrevPlayersFullInfo[tag] = \
                {'trophies': NewPlayersInfo[tag].get('trophies'), 'name': NewPlayersInfo[tag].get('name'), 'tag': tag} #type: ignore
        return TrophyDifferenceCollection

    async def Run(self):
        """
        IMPORTANT: Call self.GetPlayerList() first before calling this function.
        1. Get data from self.PlayersTag then use GET method to fetch data from coc.api
        2. Compare CurrentReceivedData with PrevReceivedData to check if players trophies changed.
        3. If it is changed, Find the trophy difference and return this value
        """
        NewPlayersInfo = await self.GetUserTrophies()
        DifferenceDetectedPlayers = self.ComparePlayerData(NewPlayersInfo)
        TrophyDifference = self.FindTrophyDifferenceAndUpdate(
            DifferenceDetectedPlayers)

        return TrophyDifference
