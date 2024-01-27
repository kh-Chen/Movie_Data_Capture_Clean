import logger

registered_event = {}
def register_event(name:str, callback):
    if name in registered_event:
        registered_event[name].append(callback)
    else:
        registered_event[name] = [callback]

def fire_event(name:str):
    logger.info("fire event "+name)
    if name in registered_event:
        for callback in registered_event[name]:
            callback()
