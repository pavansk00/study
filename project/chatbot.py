from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity, ActivityTypes

async def on_message_activity(context: TurnContext):
    text = f"You said: {context.activity.text}"
    await context.send_activity(text)

async def main(req: web.Request) -> web.Response:
    try:
        body = await req.json()
        activity = Activity().deserialize(body)
        context = TurnContext(BotFrameworkAdapter(), activity)
        if activity.type == ActivityTypes.message:
            await on_message_activity(context)
    except Exception as e:
        print(e)
    return web.Response(status=200)

if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", main)
    web.run_app(app, port=3978)
