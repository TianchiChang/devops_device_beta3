from sanic import Blueprint
from sanic.log import logger

business = Blueprint('business')

@business.route('/yuanshen')
async def starfield(request, ws):
    logger.info('Genshin Impact, power on!')