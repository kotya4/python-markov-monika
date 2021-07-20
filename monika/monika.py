import traceback
from tornado import gen
from tornado.ioloop import IOLoop
import monika.core as core

class monika :
    @classmethod
    async def coroutine ( cls ) :
        try :
            await IOLoop.current().run_in_executor ( None, core.listen )
        except Exception as e :
            print ( traceback.format_exc () )
