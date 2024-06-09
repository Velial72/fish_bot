from environs import Env


class SetEnv:
    def __init__(self) -> None:
        env = Env()
        env.read_env()

        self.tg_token = env.str('BOT_TOKEN')
        self.str_token = env.str('STR_TOKEN')
