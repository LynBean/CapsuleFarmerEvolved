
from .Config import Config
from .DataProviderThread import DataProviderThread
from .Exceptions import CapsuleFarmerEvolvedException
from .FarmThread import FarmThread
from .GuiThread import GuiThread
from .Logger import Logger
from .Restarter import Restarter
from .SharedData import SharedData
from .Stats import Stats
from .Utils import makePath
from .VersionManager import VersionManager
from pathlib import Path
from rich import print
from threading import Lock
from time import localtime, sleep, strftime
import argparse
import logging
import os
import sys

def init() -> tuple[logging.Logger, Config]:
    parser = argparse.ArgumentParser(
        description='Farm Esports Capsules by watching all matches on lolesports.com.'
    )
    parser.add_argument(
        '-c', '--config',
        dest="configPath",
        default="./config.yaml",
        help='Path to a custom config file'
    )

    args = parser.parse_args()

    makePath("logs/").mkdir(parents=True, exist_ok=True)
    makePath("sessions/").mkdir(parents=True, exist_ok=True)
    config = Config(args.configPath)
    log = Logger.createLogger(config.debug, 0.0)

    return log, config

def _main(log: logging.Logger, config: Config):
    farmThreads = {}
    refreshLock = Lock()
    locks = {"refreshLock": refreshLock}

    sharedData = SharedData()
    stats = Stats()

    for account in config.accounts:
        stats.initNewAccount(account)

    restarter = Restarter(stats)

    log.info(f"Starting a GUI thread.")
    guiThread = GuiThread(log, config, stats, locks)
    guiThread.daemon = True
    guiThread.start()

    dataProviderThread = DataProviderThread(log, config, sharedData)
    dataProviderThread.daemon = True
    dataProviderThread.start()

    while True:
        for account in config.accounts:
            if account not in farmThreads and restarter.canRestart(account) and stats.getThreadStatus(account):
                log.info(f"Starting a thread for {account}.")
                thread = FarmThread(log, config, account, stats, locks, sharedData)
                thread.daemon = True
                thread.start()
                farmThreads[account] = thread
                log.info(f"Thread for {account} was created.")

            if account in farmThreads and not stats.getThreadStatus(account):
                del farmThreads[account]

        toDelete = []

        for account in farmThreads:
            if not farmThreads[account].is_alive():
                toDelete.append(account)
                log.warning(f"Thread {account} has finished.")
                restarter.setRestartDelay(account)
                stats.updateStatus(account, f"[red]ERROR - restart at {restarter.getNextStart(account).strftime('%H:%M:%S')}, failed logins: {stats.getFailedLogins(account)}")
                log.warning(f"Thread {account} has finished and will restart at {restarter.getNextStart(account).strftime('%H:%M:%S')}. Number of consecutively failed logins: {stats.getFailedLogins(account)}")

        for account in toDelete:
            del farmThreads[account]

        sleep(5)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    log = None

    try:
        log, config = init()
        _main(log, config)

    except (KeyboardInterrupt, SystemExit):
        sys.exit()

    except CapsuleFarmerEvolvedException as e:
        if isinstance(log, logging.Logger):
            log.error(f"An error has occurred: {e}")

        else:
            print(f'[red]An error has occurred: {e}')
