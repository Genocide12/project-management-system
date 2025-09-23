import logging,sys

def configure_logging(cfg):
    level=getattr(logging,cfg.log_level.upper(),logging.INFO)
    logging.basicConfig(level=level,format='%(asctime)s %(levelname)s %(name)s: %(message)s',handlers=[logging.StreamHandler(sys.stdout)])
