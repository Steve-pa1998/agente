import logging
from datetime import datetime

log = logging.getLogger("optimizer")

def run_optimizer_cycle(state=None):   
    ts = datetime.now().isoformat(timespec="seconds")
    log.info("[optimizer] ciclo iniciado %s", ts)
    log.info("[optimizer] ciclo cerrado %s", ts)
    return state

def start_optimizer_loop():
    log.info("[optimizer] loop arrancado")
    log.info("[optimizer] loop cerrado")

run = run_optimizer_cycle
