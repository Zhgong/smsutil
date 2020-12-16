from functools import wraps
import threading
import logging

# def thread_decorator(func):
#
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         daemon_thread = threading.Thread(target=self.check_network_loop(), args=())
#         return


def authorize(allowed_id):
    logging.info("Authorize: %s" % allowed_id)

    # function decorator
    def func_deco(func):
        logging.info("Wrapper Decorating function: %s" % func.__name__)

        # function wrapper
        def check_id(update, context, *args, **kwargs):
            message = update.message
            chat_id = message.chat_id
            if chat_id == allowed_id:
                func(update, context, *args, **kwargs)
            else:
                context.bot.sendMessage(chat_id=message.chat_id, text="Do I know you?")
        return check_id
    return func_deco

