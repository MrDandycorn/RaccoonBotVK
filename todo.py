from json import load, dump
import asyncio

from credentials import vkPersUserID
from vk_botting import Cog, command, in_user_list


class Todo(Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.tasks = load(open('resources/todo.json', 'r'))
        except FileNotFoundError:
            self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        dump(self.tasks, open('resources/todo.json', 'w+'))
        return len(self.tasks)

    def remove_task(self, index):
        popped = self.tasks.pop(index-1)
        dump(self.tasks, open('resources/todo.json', 'w+'))
        return popped

    def remove_multiple(self, start, end):
        popped = []
        for num in range(start, end+1):
            popped.append(f'{num}. {self.tasks.pop(start-1)}')
        dump(self.tasks, open('resources/todo.json', 'w+'))
        return '\n'.join(popped)

    def edit_task(self, index, task):
        self.tasks[index-1] = task
        dump(self.tasks, open('resources/todo.json', 'w+'))

    def show_tasks(self):
        return '\n'.join([f'{num+1}. {task}' for num, task in enumerate(self.tasks)]) if self.tasks else 'Нет задач'

    @command()
    @in_user_list(vkPersUserID)
    async def todo(self, ctx, oper=None, *, add=None):
        if oper is None:
            return await ctx.reply(self.show_tasks())
        if oper in ['a', 'add']:
            return await ctx.reply(f'Задача {self.add_task(add)} добавлена')
        if oper in ['r', 'remove']:
            if '-' in add:
                start, end = add.split('-')
                return await ctx.reply(f'Задачи удалены:\n{self.remove_multiple(int(start), int(end))}')
            return await ctx.reply(f'Задача удалена:\n{self.remove_task(int(add))}')
        if oper in ['e', 'edit']:
            await ctx.reply(self.tasks[int(add)-1])

            def verify(m):
                return m.from_id == int(vkPersUserID)

            try:
                msg = await self.bot.wait_for('message_new', check=verify, timeout=600)
            except asyncio.TimeoutError:
                return
            if msg.text == '0':
                return
            self.edit_task(int(add), msg.text)
            return await ctx.reply(f'Изменена задача {add}')

    @command(name='test 1 2', aliases=['test 1 222'])
    async def test_command(self, ctx, *args):
        print(args)
        return await ctx.send(args)


def todo_setup(bot):
    bot.add_cog(Todo(bot))
