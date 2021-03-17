import typing

import ujson

from models import User, GlobalUser, GlobalRole, Conversation, Work, Car
from utils.consts import DatabaseActions, AccessingLevels
from utils.errors import DatabaseDeleteException, DatabaseAddException, ParseMentionException
from utils.main import get_user_from_mention


async def check_or_create(
        user_id: int, peer_id: int, warns: int = 0
) -> typing.Tuple[User, GlobalUser]:
    """
    check for user in current chat
    and global user in database
    """
    profile = await User.get_or_none(user_id=user_id, peer_id=peer_id)
    if profile is None:
        await User(user_id=user_id, peer_id=peer_id, warns=warns).save()
        profile = await User.get(user_id=user_id, peer_id=peer_id)

    global_profile = await GlobalUser.get_or_none(user_id=user_id)
    if global_profile is None:
        default_role = await GlobalRole.get(name="Default")
        await GlobalUser(user_id=user_id, global_role=default_role).save()
        global_profile = GlobalUser.get(user_id=user_id)

    return profile, global_profile


# TODO: переделать, написать парсер для value, вид value:
# name: voda, miltiplier: 100, etc.
async def add_or_remove_model(model_name: str, value: str, action: DatabaseActions) -> str:
    value = await ujson.loads(value.replace("'", '"'))
    returnable = ""
    if action == DatabaseActions.ADD:
        if model_name == "GlobalRole":
            returnable = await GlobalRole(name=value["name"]).save()
        elif model_name == "GlobalUser":
            returnable = await GlobalUser(
                user_id=value["user_id"], global_role=value["global_role"]
            ).save()
        elif model_name == "User":
            returnable = await User(**value).save()
        elif model_name == "Conversation":
            returnable = await Conversation(**value).save()
        elif model_name == "Work":
            returnable = await Work(**value).save()
        elif model_name == "Car":
            returnable = await Car(**value).save()
        else:
            raise DatabaseAddException("Addition error: no such model_name")

    elif action == DatabaseActions.REMOVE:
        try:
            if model_name == "GlobalRole":
                await GlobalRole.get(name=value["name"]).delete()
            elif model_name == "GlobalUser":
                await GlobalUser.get(
                    user_id=value["user_id"], global_role=value["global_role"]
                ).delete()
            elif model_name == "User":
                await User.get(**value).delete()
            elif model_name == "Conversation":
                await Conversation.get(**value).delete()
            elif model_name == "Work":
                await Work.get(**value).delete()
            elif model_name == "Car":
                await Car.get(**value).delete()

            returnable = "Удалено!"
        except Exception as _:
            raise DatabaseDeleteException("Deletion error")

    return str(returnable)


async def give_or_take_access(level_access: AccessingLevels, action: DatabaseActions, mention: str) -> str:
    mention = get_user_from_mention(mention)
    if not mention:
        raise ParseMentionException("Отсутствует упоминание в строке")

    if action == DatabaseActions.REMOVE:
        global_role_default = await GlobalRole.get(name="Default")
        await GlobalUser.get(user_id=mention).update(
            global_role=global_role_default
        )
        return f"{level_access.name} успешно снята!"

    elif action == DatabaseActions.ADD:
        if level_access == AccessingLevels.MODERATOR:
            global_role_moder = await GlobalRole.get(name="Moderator")
            await GlobalUser.get(user_id=mention).update(
                global_role=global_role_moder
            )
        elif level_access == AccessingLevels.ADMINISTRATOR:
            global_role_moder = await GlobalRole.get(name="Administrator")
            await GlobalUser.get(user_id=mention).update(
                global_role=global_role_moder
            )

        return f"{level_access.name} успешно выдана!"
