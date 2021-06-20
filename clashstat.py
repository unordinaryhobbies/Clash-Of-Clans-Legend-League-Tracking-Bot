import coc
import nest_asyncio
import asyncio
import os

class PlayerStats():
    def __init__(self, ID: str, Password: str) -> None:
        nest_asyncio.apply()
        self.__ID: str = ID
        self.__PW: str = Password
        self.PlayersTag: list = []
        self.client: coc.client.Client = coc.login(self.__ID, self.__PW)

    def __del__(self) -> None:
        try:
            self.client.close()
            print("Client Closed")
        except Exception:
            print("Client close failed")
        
    async def GetUserTrophies(self) -> list:
        PlayersCoroutine: list = []
        for player in self.PlayersTag:
            PlayersCoroutine.append(asyncio.create_task(self.client.get_player(player)))
            
        PlayersDataPack: list = []
        for Coroutine in PlayersCoroutine:
            PlayersDataPack.append(await Coroutine)
        
        PlayersData: list = []
        for PlayerData in PlayersDataPack:
            PlayersData.append({'name': PlayerData.name, 'tag': PlayerData.tag, 'trophies': PlayerData.trophies})
        return PlayersData

    def GetPlayerList(self, Filename: str) -> None:
        with open(Filename, 'r') as f:
            while True:
                tag = f.readline()
                tag = tag.replace('\n', '')
                if tag == '':
                    break
                self.PlayersTag.append(tag)
    
    def MakeLegendDatabase(self, PlayersInfo: list) -> None:
        for PlayerInfo in PlayersInfo:
            if os.path.isfile('{}.txt'.format(PlayerInfo.get('tag'))) is False:
                with open('{}.txt'.format(PlayerInfo.get('tag')), 'w') as f:
                    pass

    def GetPlayerLatestInfoThroughTagFile(self) -> list:
        PlayersDatabase = []
        for Tag in self.PlayersTag:
            LastestInfo = ''
            with open('{}.txt'.format(Tag), 'r') as r:
                while True:
                    PlayerData = r.readline().replace('\n', '')
                    if PlayerData == '':
                        PlayersDatabase.append({'tag': Tag, 'trophies': LastestInfo})
                        break
                    LastestInfo = PlayerData
        return PlayersDatabase
    
    def UpdateDatabase(self, PlayerInfo: dict) -> None:
        if str(PlayerInfo.get('tag')):
            if os.path.isfile('{}.txt'.format(PlayerInfo.get('tag'))) is False:
                self.MakeLegendDatabase(PlayerInfo)
            with open('{}.txt'.format(PlayerInfo.get('tag')), 'a') as a:
                a.write('{}\n'.format(PlayerInfo.get('trophies')))

    def CheckTrophyDifference(self, CurrentPlayerData, PastPlayerDataInDB) -> bool:
        if CurrentPlayerData.get('tag') == PastPlayerDataInDB.get('tag'):
            if PastPlayerDataInDB.get('trophies') == '':
                return True
            if int(PastPlayerDataInDB.get('trophies')) != int(CurrentPlayerData.get('trophies')):
                return True
            return False
        else:
            raise Exception("Tags unequal in CheckTrophyDiffernce()")

    def FindTrophyDifference(self, CurrentPlayerData: int, PastPlayerData: int) -> int:
        if CurrentPlayerData.get('tag') == PastPlayerData.get('tag'):
            try:
                TrophyDifference: int = int(CurrentPlayerData.get('trophies') - int(PastPlayerData.get('trophies')))
                return TrophyDifference
            except Exception:
                return 0
        else:
            raise Exception("Tag not found in FindTrophyDifference()")

    def Run(self) -> None:
        PlayerUpdates: list = []

        print("Getting Player List")
        self.GetPlayerList('player.txt')

        print("Fetching User Trophies")
        CurrentPlayersInfo = asyncio.run(self.GetUserTrophies())

        print("Check if file exist")
        self.MakeLegendDatabase(CurrentPlayersInfo)

        print("Get Latest Info From File")
        PastPlayersData = self.GetPlayerLatestInfoThroughTagFile()

        print("Compare Data")
        for CurrentPlayer, PastPlayer in zip(CurrentPlayersInfo, PastPlayersData):
            if self.CheckTrophyDifference(CurrentPlayer, PastPlayer):
                TrophyChange = self.FindTrophyDifference(CurrentPlayer, PastPlayer)

                if TrophyChange == 0:
                    continue
                if {'tag': CurrentPlayer.get('tag'), 'trophies': TrophyChange, 'name': CurrentPlayer.get('name')} in PlayerUpdates:
                    continue

                self.UpdateDatabase(CurrentPlayer)

                PlayerUpdates.append({'tag': CurrentPlayer.get('tag'), 'trophies': TrophyChange, 'name': CurrentPlayer.get('name')})
        
        print(PlayerUpdates)
        return PlayerUpdates