from rich.console import Console
from rich.progress import Progress
import time

console = Console()


def intro():
    """ Show intro
    """
    console.clear()
    print('\n' * 10)
    console.print("Babka 2.0")
    console.print("=" * 5, "The chosen", "=" * 5)
    loading(3)
    console.clear()


def loading(total_steps, step_name='Loading'):
    """ Simulate some loading task with a progress bar

    Args:
        total_steps (int): Number of steps to complete the task
        step_name (str, optional): Name of the task. Defaults to 'Loading'.
    """
    with Progress(console=console) as progress:
        task = progress.add_task(step_name, total=total_steps)

        for step in range(total_steps):
            progress.update(task, advance=1)
            time.sleep(0.5)  # simulate some work being done


def print_title(menu_title):
    """Show pretty menu title

    Args:
        men_title (string): Menu title
    """
    border = 80 * '='
    padding = (80 - len(menu_title)) // 2
    console.print(border)
    console.print('-' * padding + menu_title + '-' * padding, style='bold magenta')
    console.print(border)


def clear_screen():
    """Clear the console screen"""
    console.clear()

def show_menu(title, items, text1='', text2='', back=False):
    """Show menu

    Args:
        title (string): Title text
        items (list): Menu items
        text1 (str, optional): Text after title. Defaults to ''.
        text2 (str, optional): Text after text after title. Defaults to ''.
        back (bool, optional): Show back button. Defaults to False.

    Returns:
        int: Selected menu item
    """
    print_title(title)
    if text1:
        console.print(text1)
    if text2:
        console.print(text2)

    for index, item in enumerate(items, start=1):
        console.print(f"[{index}] {item}")

    if back:
        console.print("[0] Back")

    while True:
        choice = console.input("[bold yellow]Выбери пункт: [/bold yellow]")
        if choice.isdigit() and (0 <= int(choice) <= len(items) if back else 1 <= int(choice) <= len(items)):
            return int(choice)
        console.print("[bold red]Неверный ввод. Попробуй ещё.[/bold red]")
